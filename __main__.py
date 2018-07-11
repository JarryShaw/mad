# -*- coding: utf-8 -*-
"""MAD -- Malicious Application Detector

/usr/local/mad
    |-- dataset                                 # where all dataset go
    |   |-- YYYY-MM-DDTHH:MM:SS.US              # dataset named after ISO timestamp
    |   |   |-- fingerprint.json                # fingerprint filter report
    |   |   |-- index.json                      # TCP flow index record
    |   |   |-- record.json                     # WebGraphic group record
    |   |   |-- Background_PC                   # where Background_PC dataset files go
    |   |       |-- 0                           # clean ones
    |   |       |   |-- IP_PORT-IP_PORT-TS.dat  # dataset file
    |   |       |   |-- ...
    |   |       |-- 1                           # malicious ones
    |   |       |   |-- IP_PORT-IP_PORT-TS.dat  # dataset file
    |   |       |   |-- ...
    |   |-- ...
    |-- model                                   # where CNN model go
    |-- retrain                                 # where CNN retrain dataset go
    |-- mad.log                                 # log file for RPC
"""
import collections
import datetime as dt
import json
import multiprocessing
import os
import pathlib
import signal
import subprocess
import sys

import pcapkit.all
import scapy.all

from fingerprints.fingerprintsManager import *
from StreamManager.StreamManager4 import *
from webgraphic.webgraphic import *


ROOT = os.path.dirname(os.path.abspath(__file__))
                    # file root path
MODE = 3            # 1-initialisation; 2-migeration; 3-prediction; 4-adaptation
PATH = '/'          # path of original data
IFACE = 'eth0'      # sniff interface
# TIMEOUT = 1000      # sniff timeout
TIMEOUT = 15        # sniff timeout
RETRAIN = False     # retrain flag


FLOW_DICT = {
    # 'Browser_PC' : lambda stream: stream.GetBrowserGroup_PC(),
    'Background_PC' : lambda stream: stream.GetBackgroudGroup_PC(),
    # 'Browser_Phone' : lambda stream: stream.GetBrowserGroup_Phone(),
    'Background_Phone' : lambda stream: stream.GetBackgroudGroup_Phone(),
    'Suspicious' : lambda stream: stream.GetSuspicious(),
}


def main(*, iface=None, mode=None, path=None):
    """Main interface for MAD."""
    signal.signal(signal.SIGUSR1, make_worker)
    signal.signal(signal.SIGUSR2, retrain_cnn)

    if iface is not None:
        global IFACE
        IFACE = iface

    if mode is not None:
        global MODE
        MODE = mode

    if mode != 3:
        global PATH
        PATH = path

    make_worker()


def retrain_cnn(*args):
    """Retrain the CNN model."""
    # if already under retrain do nothing
    global RETRAIN
    if RETRAIN:     return

    # update retrain flag
    global MODE
    RETRAIN = True
    MODE = 4

    # start retrain
    multiprocessing.Process(
        target=run_cnn,
        kwargs={'path': '/usr/local/mad/retrain'},
    ).start()


def make_worker(*args):
    """Create child process."""
    if MODE == 3:
        return multiprocessing.Process(target=start_worker).start()

    # do initialisation or migration first
    # then, keep on with prediction (if need)
    start_worker()
    if MODE == 2:
        global MODE
        MODE = 3
        return make_worker()


def start_worker():
    """Start child process."""
    # above all, create directory for new dataset
    # and initialise fingerprint manager
    path = pathlib.Path(f'/usr/local/mad/dataset/{dt.datetime.now().isoformat()}')
    path.mkdir(parents=True, exist_ok=True)
    fp = fingerprintManager()

    print(f'New process start @ {path}')

    # write a log file to inform state of running
    # the back-end of webpage shall check this file
    with open('/usr/local/mad/mad.log', 'at', 1) as file:
        file.write(f'0 start@{path}\n')

    # first, we sniff packets using Scapy
    # or load data from an existing PCAP file
    sniffed = make_sniff()

    # now, we send a signal to the parent process
    # to create a new process and continue
    # os.kill(os.getppid(), signal.SIGUSR1)

    # then, we trace and make index for TCP flow of packets sniffed
    # using PyPCAPKit, whose interface is now done
    index = make_flow(sniffed, path=path)

    # generate WebGraphic & fingerprints for each flow
    # through reconstructed functions and methods
    group = make_group(sniffed, index, fp, path=path)

    # and make dataset for each flow in accordance with the group
    # using PyPCAPKit with its reassembly interface
    make_dataset(sniffed, group, fp, path=path)

    # and now, time for the neural network
    # reports should be placed in a certain directory
    run_cnn(path=path)

    # afterwards, write a log file to record state of accomplish
    # the back-end of webpage shall check this file periodically
    with open('/usr/local/mad/mad.log', 'at', 1) as file:
        file.write(f'0 stop@{path}\n')


def make_sniff():
    """Load data or sniff packets."""
    if MODE == 3:
        return scapy.all.sniff(offline='../../PyPCAPKit/sample/http3.pcap')
        return scapy.all.sniff(timeout=TIMEOUT)
        # return scapy.all.sniff(timeout=TIMEOUT, iface=IFACE)

    if pathlib.Path(PATH).is_file():
        return scapy.all.sniff(offline=PATH)

    sniffed = list()
    for file in os.listdir(PATH):
        try:
            sniffed.extend(scapy.all.sniff(offline=f'{PATH}/{file}'))
        except scapy.error.Scapy_Exception as error:
            print('Error:', error)
    return sniffed


def make_flow(sniffed, *, path):
    """Insert UA key to TraceFlow index."""
    print(f'Tracing TCP flow @ {path}')
    # TraceFlow
    traceflow = pcapkit.trace()
    for count, packet in enumerate(sniffed):
        flag, data = pcapkit.scapy_tcp_traceflow(packet, count=count)
        if flag:    traceflow(data)
    traceindex = traceflow.index

    def get_url(analysis):
        """Make URL of HTTP request."""
        if analysis.info.receipt == 'request':
            host = analysis.info.header.get('Host', str())
            uri = analysis.info.header.request.target
            url = host + uri
            return utl

    # Analysis
    index = list()
    for flow in traceindex:
        hostlist = list()
        templist = list()
        for number in flow.index:
            analysis = pcapkit.analyse(file=bytes(sniffed[number]['TCP'].payload))
            if pcapkit.protocols.application.httpv1.HTTPv1 in analysis.protochain:
                templist.append(analysis.info.header.get('User-Agent', 'UnknownUA'))
                hostlist.append(get_url(analysis))
            else:
                templist.append('UnknownUA')
        index.append(pcapkit.all.Info(flow, url=tuple(filter(None, set(hostlist))),
                        ua=collections.Counter(templist).most_common(1)[0][0]))

    with open(f'{path}/index.json', 'w') as file:
        json.dump(index, file)

    return tuple(index)


def make_group(sniffed, index, fp, *, path):
    """Generate WebGraphic and fingerprints."""
    print(f'Now grouping packets @ {path}')
    # WebGraphic
    builder = webgraphic()
    builder.read_in(sniffed)
    IPS = builder.GetIPS()

    # StreamManager
    stream = StreamManager(index, sniffed)
    stream.classify(IPS)
    stream.Group()
    if MODE != 3:
        stream.labelGroups()

    # load labels
    record = dict()
    for kind, group in FLOW_DICT.items():
        record[kind] = group(stream)

    # fingerprints
    if MODE != 3:
        for label in record.values():
            fp.GenerateAndUpdate(sniffed, label)

    # dump record
    with open(f'{path}/record.json', 'w') as file:
        json.dump(record, file)

    return record


def make_dataset(sniffed, labels, fp, *, path):
    """Make dataset."""
    print(f'Making dataset @ {path}')
    fplist = list()
    for kind, group in labels.items():
        # only make dataset for type Background PC
        if kind != 'Background_PC':     continue

        # make directory
        pathlib.Path(f'{path}/{kind}/0').mkdir(parents=True, exist_ok=True)  # safe
        pathlib.Path(f'{path}/{kind}/0').mkdir(parents=True, exist_ok=True)  # malicious

        # identify figerprints
        group_keys = group.keys()
        if MODE == 3:
            fpreport = fp.Identify(sniffed, group)
            for ipua in fpreport['is_malicious']:
                fplist += group[ipua]
            group_keys = fpreport['new_app']

        # enumerate files
        for ipua in group_keys:
            for file in group[ipua]:
                label = int(file['type'])
                fname = f"{file['label']}.dat"

                # remove existing files
                if pathlib.Path(fname).exists():
                    os.remove(fname)

                # reassembly packets
                reassembly = pcapkit.reassemble(protocol='TCP', strict=True)
                for number in file['index']:
                    flag, data = pcapkit.scapy_tcp_reassmbly(sniffed[number], count=number)
                    if flag:    reassembly(data)
                
                # dump dataset
                for packet in reassembly.packets:
                    if pcapkit.protocols.application.httpv1.HTTPv1 in packet.protochain:
                        with open(fname, 'ab') as file:
                            file.write(packet.info.raw.header or None)

    # fingerprint report
    with open(f'{path}/fingerprint.json', 'w') as file:
        json.dump(fpreport, file)


def run_cnn(*, path):
    """Create subprocess to run CNN model."""
    cmd = [sys.executable, os.path.join(ROOT, 'Training.py'),
            path, '/usr/local/mad/model', MODE, 'Background_PC', os.getppid()]
    subprocess.run(cmd)


if __name__ == '__main__':
    sys.exit(start_worker())
