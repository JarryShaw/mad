# -*- coding: utf-8 -*-
"""MAD -- Malicious Application Detector

/mad/
    |-- mad.log                                 # log file for RPC (0-start; 1-stop; 2-retrain; 3-ready)
    |-- fingerprint.pickle                      # pickled fingerprint database
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
    |-- report/                                 # where CNN prediction report go
    |   |-- Background_PC/                      # Background_PC reports
    |   |   |-- index.json                      # report index file
    |   |   |-- YYYY-MM-DDTHH:MM:SS.US.json     # report named after dataset
    |   |-- ...
    |-- model/                                  # where CNN model go
    |   |-- Background_PC/                      # Background_PC models
    |   |   |-- ...
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
import collections
import contextlib
import datetime as dt
import functools
import json
import multiprocessing
import os
import pathlib
import shlex
import shutil
import signal
import subprocess
import sys
import time
import traceback

from fingerprints.fingerprintsManager import fingerprintManager
from make_stream import JSONEncoder, dump_stream, load_stream, object_hook
from StreamManager.StreamManager4 import StreamManager
from utils import JSONEncoder, object_hook
from webgraphic.webgraphic import webgraphic

# # import chardet
# # import pcapkit.all
# import scapy.all


@functools.total_ordering
class minstr:

    def __lt__(self, value):
        if isinstance(value, str):
            return True
        return NotImplemented


# # testing macros
# FILE = NotImplemented
# COUNT = -1

# PID
PID = os.getpid()
# file root path
ROOT = os.path.dirname(os.path.abspath(__file__))
# 1-initialisation; 2-migration; 3-prediction; 4-adaptation; 5-regeneration
MODE = 3
# path of input data
PATH = NotImplemented
# list of data files
LIST = NotImplemented
# list offset
COUNT = -1
# latest processing file name
MAX_FILE = minstr
# # sniff interface
# IFACE = 'eth0'
# file lock
LOCK = multiprocessing.Lock()
# retrain flag
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
        except BaseException:
            if MODE != 3:
                raise
            with contextlib.suppress(OSError):
                os.kill(PID, signal.SIGUSR1)
            traceback.print_exc()
    return wrapper


def main(mode=None, path=None):
    """Main interface for MAD."""
    print(f'Manager process: {PID}')

    # bind signals
    signal.signal(signal.SIGUSR1, make_worker)
    signal.signal(signal.SIGUSR2, retrain_cnn)

    # make paths
    for name in {'dataset', 'model', 'retrain'}:
        pathlib.Path(f'/mad/{name}').mkdir(parents=True, exist_ok=True)

    # if iface is not None:
    #     global IFACE
    #     IFACE = iface

    if mode is not None:
        global MODE
        MODE = mode

    if path is not None:
        global PATH
        PATH = path

    # if file is not None:
    #     global FILE
    #     with open(file, 'r') as file:
    #         FILE = json.load(file, object_hook=object_hook)

    # update file list
    global LIST
    LIST = sorted(f'{PATH}/{file}' for file in os.listdir(PATH))

    # check log file
    global MAX_FILE
    if os.path.isfile('/mad/mad.log'):
        with open('/mad/mad.log') as file:
            for line in filter(lambda l: l.startswith('1'), file):
                _, _, name, _ = line.split(' ')
        MAX_FILE = name

    # start procedure
    make_worker()
    while True:
        # if FILE is not NotImplemented \ ###
        #     and COUNT >= len(FILE): break ###
        time.sleep(10*60)
        global COUNT
        if COUNT >= len(LIST):
            NEW_LIST = sorted(f'{PATH}/{file}' for file in os.listdir(PATH))
            if NEW_LIST == LIST:
                continue
            COUNT = len(NEW_LIST)
            for index, name in enumerate(NEW_LIST, start=-1):
                path = f"/mad/dataset/{os.path.splitext(os.path.split(name)[1])[0].replace(' ', '-')}"
                if path > MAX_FILE:
                    COUNT = index
                    break
            LIST = NEW_LIST


def retrain_cnn(*args):
    """Retrain the CNN model."""
    # if already under retrain do nothing
    if RETRAIN.value:
        return
    # return ###

    # update retrain flag
    RETRAIN.value = True

    # start retrain
    multiprocessing.Process(
        target=run_cnn,
        kwargs={'path': '/mad/retrain',
                'retrain': True},
    ).start()


def make_worker(*args):
    """Create child process."""
    # start child in prediction
    global MODE, COUNT, MAX_FILE
    if MODE == 3:
        # if FILE is not NotImplemented:
        #     COUNT += 1
        #     if COUNT >= len(FILE):
        #         return
        COUNT += 1
        if COUNT >= len(LIST):
            return
        MAX_FILE = LIST[COUNT]
        return multiprocessing.Process(target=start_worker).start()

    # do initialisation or migration first
    # then, keep on with prediction (if need)
    start_worker()
    if MODE in (2, 5):
        MODE = 3
        return make_worker()


@beholder
def start_worker():
    """Start child process."""
    if MODE == 3:
        name = make_sniff(path=NotImplemented)
        dsname = os.path.splitext(os.path.split(name)[1])[0].replace(' ', '-')
    else:
        dsname = dt.datetime.now().isoformat()

    # above all, create directory for new dataset
    # and initialise fingerprint manager
    path = pathlib.Path(f'/dataset/{dsname}')
    path.mkdir(parents=True, exist_ok=True)
    fp = fingerprintManager()

    print(f'New mode_{MODE} process start @ {path}')

    # write a log file to inform state of running
    # the back-end of webpage shall check this file
    with LOCK:
        with open('/mad/mad.log', 'at', 1) as file:
            file.write(f'0 {dt.datetime.now().isoformat()} {path} {MODE}\n')

    milestone_0 = time.time()

    # first, we sniff packets using Scapy
    # or load data from an existing PCAP file
    if MODE != 3:
        name = make_sniff(path=path)

    milestone_1 = time.time()
    print(f'Sniffed for {milestone_1-milestone_0} seconds')

    # # now, we send a signal to the parent process
    # # to create a new process and continue
    # if MODE == 3 and FILE is NotImplemented:
    #     os.kill(PID, signal.SIGUSR1)

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
            file.write(f'1 {dt.datetime.now().isoformat()} {path} {MODE}\n')

    # finally, remove used temporary dataset files
    # but record files should be reserved for further usage
    for name in {'Background_PC', 'stream', 'tmp'}:
        with contextlib.suppress(FileNotFoundError):
            shutil.rmtree(os.path.join(path, name))

    milestone_5 = time.time()
    print(f'Worked for {milestone_5-milestone_0} seconds')


def make_sniff(path):
    """Load data or sniff packets."""
    # just sniff when prediction
    if MODE == 3:
        # return '/data/wanyong-httpdump/20180408/20180309/wanyong.pcap000' ###
        # if FILE is NotImplemented:
        #     name = f'/usr/local/mad/pcap/{pathlib.Path(path).name}.pcap'
        #     sniffed = scapy.all.sniff(timeout=TIMEOUT, iface=IFACE)
        #     scapy.all.wrpcap(name, sniffed)
        #     return name
        # print(f"Now it's time for No.{COUNT} {FILE[COUNT]}")
        # return FILE[COUNT]
        print(f"Now it's time for No.{COUNT} {LIST[COUNT]}")
        return LIST[COUNT]

    # # extract file, or ...
    # if pathlib.Path(PATH).is_file():
    #     return PATH

    # # files in a directory
    # sniffed = list()
    # for file in os.listdir(PATH):
    #     try:
    #         sniffed.extend(scapy.all.sniff(offline=f'{PATH}/{file}'))
    #     except scapy.error.Scapy_Exception as error:
    #         print('Error:', error)
    # name = f'/usr/local/mad/pcap/{pathlib.Path(path).name}.pcap'
    # scapy.all.wrpcap(name, sniffed)
    # return name

    raise NotImplementedError


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
        json.dump(record, file, cls=JSONEncoder)

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
        # pathlib.Path(f'/mad/report/{kind}').mkdir(parents=True, exist_ok=True)
        # pathlib.Path(f'/usr/local/mad/retrain/stream/{kind}/0').mkdir(parents=True, exist_ok=True)
        # pathlib.Path(f'/usr/local/mad/retrain/stream/{kind}/1').mkdir(parents=True, exist_ok=True)
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
                json.dump(fpreport, file, cls=JSONEncoder)

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

    # send signals
    if MODE == 3:
        try:
            os.kill(PID, signal.SIGUSR1)
        except ProcessLookupError:
            traceback.print_exc()

    # run CNN subprocess
    for kind in {'Background_PC', }:
        cmd = [sys.executable, shlex.quote(os.path.join(ROOT, 'Training.py')),
               str(path), f'/mad/model/{kind}/', MODE_DICT[mode], kind, str(PID)]
        # print(cmd) ###
        subprocess.run(cmd)

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

        # reset flag after retrain procedure
        RETRAIN.value = False


if __name__ == '__main__':
    sys.exit(main())
