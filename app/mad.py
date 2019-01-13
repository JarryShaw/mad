# -*- coding: utf-8 -*-
"""MAD -- Malicious Application Detector

/mad/
    |-- mad.log                                 # log file for RPC (0-start; 1-stop; 2-retrain; 3-ready; 4-error)
    |-- fingerprint.pickle                      # pickled fingerprint database
    |-- pcap/
    |   |-- apt_log.txt                         # log file
    |   |-- YYYY_MMDD_HHMM_SS.pcap              # PCAP files
    |   |-- ...
    |-- dataset/                                # where all dataset go
    |   |-- YYYY-MM-DDTHH:MM:SS.US/             # dataset named after ISO timestamp
    |   |   |-- groups.json                     # WebGraphic group record
    |   |   |-- filter.json                     # fingerprint filter report
    |   |   |-- record.json                     # flattened group record
    |   |   |-- stream.json                     # backup for stream.json in retrain
    |   |   |-- tmp/                            # temporary files generated by pkt2flow
    |   |   |   |-- tcp_syn/
    |   |   |   |   |-- IP_PORT_IP_PORT_TS.pcap
    |   |   |   |   |-- ...
    |   |   |   |-- tcp_nosyn/
    |   |   |   |   |-- IP_PORT_IP_PORT_TS.pcap
    |   |   |   |   |-- ...
    |   |   |-- stream/                         # where stream files go
    |   |   |   |-- IP_PORT_IP_PORT_TS.pcap     # temporary stream PCAP files
    |   |   |   |-- ...
    |   |   |-- Background_PC/                  # where Background_PC dataset files go
    |   |       |-- 0/                          # clean ones
    |   |       |   |-- IP_PORT_IP_PORT_TS.dat  # dataset file
    |   |       |   |-- ...
    |   |       |-- 1/                          # malicious ones
    |   |           |-- IP_PORT_IP_PORT_TS.dat  # dataset file
    |   |           |-- ...
    |   |-- ...
    |-- model/                                  # where CNN model go
    |   |-- Background_PC/                      # Background_PC models
    |   |   |-- ...
    |   |-- ...
    |-- report/                                 # where generated reports go
    |   |-- ...
    |-- retrain/                                # where CNN retrain data go
        |-- Background_PC/                      # Background_PC retrain dataset
        |   |-- 0/                              # clean ones
        |   |   |-- YYYY-MM-DDTHH:MM:SS.US_IP_PORT_IP_PORT_TS.dat
        |   |   |-- ...
        |   |-- 1/                              # malicious ones
        |       |-- YYYY-MM-DDTHH:MM:SS.US_IP_PORT_IP_PORT_TS.dat
        |       |-- ...
        |-- stream.json                         # stream index for retrain

"""
import argparse
import ast
import collections
import contextlib
import datetime as dt
import functools
import json
import math
import os
import pathlib
import pprint  # ##
import shlex
import shutil
import signal
import subprocess
import sys
import time
import traceback
import warnings

import dpkt
import scapy.all

from fingerprints.fingerprintsManager import fingerprintManager
from jsonutils import JSONEncoder, object_hook
from make_stream import JSONEncoder, dump_stream, load_stream, object_hook
from SQLManager import getProcessedFile, saveProcessedFile
from SQLManager.Model import minstr
from StreamManager.StreamManager4 import StreamManager
from webgraphic.webgraphic import webgraphic

try:
    import threading
except ImportError:
    import dummy_threading as threading

# CPU number
try:        # try first
    import multiprocessing
except ImportError:
    multiprocessing = None
    proc_cnt = 0
    warnings.showwarning('current system has not multiprocessing support',
                         ResourceWarning, filename=__file__, lineno=87)
else:       # CPU number if multiprocessing supported
    proc_cnt = ast.literal_eval(os.environ['PROC_CNT'])
finally:
    CPU_CNT = proc_cnt

# PID
PID = os.getpid()
# file root path
ROOT = os.path.dirname(os.path.abspath(__file__))
# 1-initialisation; 2-migration; 3-prediction; 4-adaptation; 5-regeneration
MODE = 3
# path of input data
PATH = '/mad/pcap'
# latest processing file name
MAX_FILE = getProcessedFile()
# devel flag
DEVEL = ast.literal_eval(os.environ['MAD_DEVEL'])
# wait timeout
TIMEOUT = ast.literal_eval(os.environ['MAD_TIMEOUT'])
# sampling interval
INTERVAL = ast.literal_eval(os.environ['MAD_INTERVAL'])

# current proc info
if multiprocessing is None:
    PROC = threading.local()
    PROC.src = '<undefined>'
    PROC.dst = '<undefined>'
else:
    PROC = argparse.Namespace(
        src='<undefined>',
        dst='<undefined>'
    )

# file lock
if multiprocessing is None:
    LOCK = threading.Lock()
else:
    LOCK = multiprocessing.Lock()

# retrain flag
if multiprocessing is None:
    RETRAIN = argparse.Namespace(value=False)
else:
    RETRAIN = multiprocessing.Value('B', False)

FLOW_DICT = {
    # 'Browser_PC': lambda stream: stream.GetBrowserGroup_PC(),
    'Background_PC': lambda stream: stream.GetBackgroundGroup_PC(),
    # 'Browser_Phone': lambda stream: stream.GetBrowserGroup_Phone(),
    'Background_Phone': lambda stream: stream.GetBackgroundGroup_Phone(),
    'Suspicious': lambda stream: stream.GetSuspicious(),
}

MODE_DICT = {
    1: 'train',    # initialisation
    2: 'retrain',  # migration
    3: 'predict',  # prediction
    4: 'retrain',  # adaptation
}


def beholder(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BaseException as error:
            with LOCK:
                with open('/mad/mad.log', 'at', 1) as file:
                    file.write(f'4 {dt.datetime.now().isoformat()} {PROC.src} {PROC.dst} {MODE} {error.args}\n')
                with open('/mad/pcap/apt_log.txt', 'at', 1) as file:
                    file.write(f'4 {dt.datetime.now().isoformat()} {PROC.src} {PROC.dst} {MODE} {error.args}\n')
            if MODE != 3:
                raise
            elif DEVEL:
                sys.exit(traceback.format_exc())
            else:
                traceback.print_exc()
            return minstr()
    return wrapper


def main(mode=3, path='/mad/pcap', sample=None):
    """Main interface for MAD."""
    print(f'Manager process: {PID}')

    # bind signals
    # signal.signal(signal.SIGUSR1, make_worker)
    signal.signal(signal.SIGUSR2, retrain_cnn)

    # make paths
    for name in {'dataset', 'model', 'retrain'}:
        pathlib.Path(f'/mad/{name}').mkdir(parents=True, exist_ok=True)

    # set PATH
    global PATH
    PATH = path

    # set MODE
    global MODE
    MODE = mode

    # check log file
    global MAX_FILE
    # if os.path.isfile('/mad/mad.log'):
    #     name = MAX_FILE
    #     with open('/mad/mad.log') as file:
    #         for line in filter(lambda l: l.startswith('1'), file):
    #             _, _, _, name, _ = shlex.split(line)
    #     MAX_FILE = name
    print(f'Current MAX_FILE: {MAX_FILE!r}')

    def _validate_pcap(entry):
        if entry.is_file():
            try:
                with open(entry.path, 'rb') as file:
                    dpkt.pcap.Reader(file)
                return True
            except (ValueError, dpkt.dpkt.Error):
                return False
        return False

    def _sampling(filelist):
        if INTERVAL == 0:
            return sorted(filelist)
        pool = list()
        modulus = INTERVAL + 1
        for index, filename in enumerate(sorted(filelist)):
            if index % modulus == 0:
                pool.append(filename)
        return sorted(pool)

    # update file list
    filelist = list()
    for item in filter(lambda e: _validate_pcap(e), os.scandir(PATH)):
        filename = item.path
        print(filename, (filename <= MAX_FILE))
        if filename <= MAX_FILE:
            continue
        filelist.append(filename)

    # start procedure
    pool = _sampling(filelist)
    make_worker(pool, sample=sample)
    with contextlib.suppress(ValueError):
        MAX_FILE = max(pool)
    print(f'Current MAX_FILE: {MAX_FILE!r}')

    # break in devel mode or others
    if DEVEL or MODE != 3:
        print('Quit on demand')
        return

    # enter main loop
    while True:
        print(f'Wait for another {TIMEOUT} second(s) before next round.')
        time.sleep(TIMEOUT)

        # update file pool
        filelist = list()
        for item in filter(lambda e: _validate_pcap(e), os.scandir(PATH)):
            filename = item.path
            if filename <= MAX_FILE:
                continue
            filelist.append(filename)
        pool = _sampling(filelist)

        # start new round
        make_worker(pool)
        with contextlib.suppress(ValueError):
            MAX_FILE = max(pool)
        print(f'Current MAX_FILE: {MAX_FILE!r}')


def retrain_cnn(*args):
    """Retrain the CNN model."""
    # if already under retrain do nothing
    if RETRAIN.value:
        return
    # return ###

    # update retrain flag
    RETRAIN.value = True

    # start retrain
    if multiprocessing is None:
        threading.Thread(
            target=run_cnn,
            kwargs={'path': '/mad/retrain',
                    'retrain': True}
        ).start()
    else:
        multiprocessing.Process(
            target=run_cnn,
            kwargs={'path': '/mad/retrain',
                    'retrain': True},
        ).start()


def make_worker(pool, sample=None):
    """Create child process."""
    # not implemented
    global MODE
    if not (1 <= MODE <= 5):
        raise NotImplementedError

    # start child in prediction
    # using worker Pool or sequential solution
    if MODE == 3:
        print('Current worker pool:')
        pprint.pprint(pool)
        if pool:
            if CPU_CNT <= 1:
                filelist = [start_worker(file) for file in pool]
            else:
                filelist = multiprocessing.Pool(processes=CPU_CNT).map(start_worker, pool)
        else:
            filelist = list()
            print(f'No PCAP files in the pool, wait for another {TIMEOUT} second(s).')
        return filelist

    # or force to run retrain process
    if MODE == 4:
        return retrain_cnn()

    # do initialisation or migration first
    # then, keep on with prediction (if need)
    start_worker(sample)
    if MODE in (2, 5):
        MODE = 3
        return make_worker(pool)


@beholder
def start_worker(path):
    """Start child process."""
    milestone_0 = time.time()

    # first, we sniff packets using Scapy
    # or load data from an existing PCAP file
    name = make_sniff(path)
    osname = shlex.quote(name)
    dsname = shlex.quote(os.path.split(name)[1])
    # pobj = pathlib.Path(name)
    # stem = pathlib.Path(name).stem
    # if pobj.suffix != '.pcap':
    #     pext = pobj.suffix.strip('.pcap')
    #     dsname = shlex.quote(f'{stem}_{pext}')
    # else:
    #     dsname = shlex.quote(pathlib.Path(name).stem)
    PROC.src = name
    PROC.dst = osname

    # create directory for new dataset
    # and initialise fingerprint manager
    path = pathlib.Path(f'/mad/dataset/{dsname}')
    path.mkdir(parents=True, exist_ok=True)
    fp = fingerprintManager()

    print(f'New mode_{MODE} process start @ {path}')

    # write a log file to inform state of running
    # the back-end of webpage shall check this file
    with LOCK:
        with open('/mad/mad.log', 'at', 1) as file:
            file.write(f'0 {dt.datetime.now().isoformat()} {path} {osname} {MODE}\n')
        with open('/mad/pcap/apt_log.txt', 'at', 1) as file:
            file.write(f'0 {dt.datetime.now().isoformat()} {path} {osname} {MODE}\n')

    milestone_1 = time.time()
    print(f'Bootstrapped for {milestone_1-milestone_0} seconds')

    # then, generate WebGraphic & fingerprints for each flow
    # through reconstructed functions and methods
    group = make_group(name, fp, path=path)

    milestone_2 = time.time()
    print(f'Grouped for {milestone_2-milestone_1} seconds')

    # and make dataset for each flow in accordance with the group
    # using PyPCAPKit with its reassembly interface
    if MODE != 5:
        make_dataset(group, fp, path=path)

    milestone_3 = time.time()
    print(f'Dumped for {milestone_3-milestone_2} seconds')

    # and now, time for the neural network
    # reports should be placed in a certain directory
    if MODE != 5:
        run_cnn(path=path)

    milestone_4 = time.time()
    print(f'Predicted for {milestone_4-milestone_3} seconds')

    # afterwards, write a log file to record state of accomplish
    # the back-end of webpage shall check this file periodically
    with LOCK:
        with open('/mad/mad.log', 'at', 1) as file:
            file.write(f'1 {dt.datetime.now().isoformat()} {path} {osname} {MODE}\n')
        saveProcessedFile(name, f'/mad/dataset/{dsname}/report.json')
        with open('/mad/pcap/apt_log.txt', 'at', 1) as file:
            file.write(f'1 {dt.datetime.now().isoformat()} {path} {osname} {MODE}\n')

    # # also, send a signal to update the database
    # # this is only for prediction mode
    # if MODE == 3:
    #     os.kill(PID, signal.SIGUSR1)

    # finally, remove used temporary dataset files
    # but record files should be reserved for further usage
    if DEVEL:
        print(f'Not to remove temporary files @ {str(path)!r}.')
    else:
        for name in {'Background_PC', 'stream', 'tmp'}:
            with contextlib.suppress(FileNotFoundError):
                shutil.rmtree(os.path.join(str(path), name))

    milestone_5 = time.time()
    print(f'Worked for {milestone_5-milestone_0} seconds')

    # return processed file
    return name


def make_sniff(path):
    """Load data or sniff packets."""
    # just sniff when prediction
    if MODE == 3:
        print(f"Now it's time for {path}")
        return path

    # extract file, or ...
    if os.path.isfile(path):
        return path

    # files in a directory
    sniffed = list()
    for item in os.scandir(path):
        try:
            sniffed.extend(scapy.all.sniff(offline=item.path))
        except scapy.error.Scapy_Exception:
            traceback.print_exc()
    name = f'/mad/pcap/{os.path.split(path)[0]}.pcap'
    scapy.all.wrpcap(name, sniffed)
    return name


def make_group(name, fp, path):
    """Generate WebGraphic and fingerprints."""
    print(f'Now grouping packets @ {path}')

    # WebGraphic
    builder = webgraphic()
    builder.read_in(name)
    IPS = builder.GetIPS()

    # StreamManager
    stream = StreamManager(name, str(path))
    stream.generate()
    stream.classify(IPS)
    stream.Group()
    if MODE != 3:
        stream.labelGroups()

    # labels & fingerprints
    record = dict()
    for kind, group in FLOW_DICT.items():
        groups = group(stream)
        record[kind] = groups
        if MODE != 3:
            fp.GenerateAndUpdate(f'{path}/stream', groups)

    # dump record
    dump_stream(record, path=path)
    with open(f'{path}/groups.json', 'w') as file:
        json.dump(record, file, cls=JSONEncoder, indent=2)

    return record


def make_dataset(labels, fp, path):
    """Make dataset."""
    print(f'Making dataset @ {path}')

    fplist = list()
    for kind, group in labels.items():
        if kind != 'Background_PC':
            continue

        # make directory
        pathlib.Path(f'{path}/{kind}/0').mkdir(parents=True, exist_ok=True)  # safe
        pathlib.Path(f'{path}/{kind}/1').mkdir(parents=True, exist_ok=True)  # malicious
        pathlib.Path(f'/mad/retrain/{kind}/0').mkdir(parents=True, exist_ok=True)
        pathlib.Path(f'/mad/retrain/{kind}/1').mkdir(parents=True, exist_ok=True)

        # identify fingerprints
        group_keys = group.keys()
        if MODE == 3:
            fpreport = fp.Identify(f'{path}/stream', group)
            for ipua in fpreport['is_malicious']:
                fplist += group[ipua]
            group_keys = fpreport['new_app']

            # fingerprint report
            with open(f'{path}/filter.json', 'w') as file:
                json.dump(fpreport, file, cls=JSONEncoder, indent=2)

        # enumerate files
        for ipua in group_keys:
            # print(ipua, group[ipua])
            for file in group[ipua]:
                label = pathlib.Path(file['filename']).stem
                ftype = int(file['is_malicious'])
                fname = f'{path}/{kind}/{ftype}/{label}.dat'

                # remove existing files
                if os.path.exists(fname):
                    os.remove(fname)

                size = 0
                for payload in file['http']:
                    if size > 1024:
                        break
                    with open(fname, 'ab') as file:
                        byte = payload.split(b'\r\n\r\n')[0]
                        size += len(byte)
                        file.write(byte)
                        print(file.name)


def run_cnn(path, retrain=False):
    """Create subprocess to run CNN model."""
    print(f"CNN running @ {path}")

    # check mode for CNN
    mode = 4 if retrain else MODE

    # write log for start retrain
    if retrain:
        with LOCK:
            with open('/mad/mad.log', 'at', 1) as file:
                file.write(f'2 {dt.datetime.now().isoformat()} {path} {mode}\n')
            with open('/mad/pcap/apt_log.txt', 'at', 1) as file:
                file.write(f'2 {dt.datetime.now().isoformat()} {path} {mode}\n')

    # run CNN subprocess
    for kind in {'Background_PC', }:
        cmd = [sys.executable, shlex.quote(os.path.join(ROOT, 'Training.py')),
               str(path), f'/mad/model/{kind}/', MODE_DICT[mode], kind, str(PID)]
        try:
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            traceback.print_exc()

    # things to do when retrain
    if retrain:
        # load group record
        record = load_stream()

        # update fingerprints
        fp = fingerprintManager()
        for kind in {'Background_PC', }:
            fp.GenerateAndUpdate(NotImplemented, record[kind])

        # write log for stop retrain
        with LOCK:
            with open('/mad/mad.log', 'at', 1) as file:
                file.write(f'3 {dt.datetime.now().isoformat()} {path} {mode}\n')
            with open('/mad/mad.log', 'at', 1) as file:
                file.write(f'3 {dt.datetime.now().isoformat()} {path} {mode}\n')

        # reset flag after retrain procedure
        RETRAIN.value = False


if __name__ == '__main__':
    sys.exit(main())
