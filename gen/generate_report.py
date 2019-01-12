#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools
import getopt
import json
import math
import os
import pprint  # ##
import sys
import time
import warnings

from generator import (updateActiveSoftware, updateConnection,
                       updateInfectedComputer, updateLoss)
from server_map import updateServerMap
from SQLManager import (deleteToBeProcessedFile, getLoss, getToBeProcessedFile,
                        updateToBeProcessedFile)

try:
    import multiprocessing
except ImportError:
    warnings.showwarning('current system has not multiprocessing support',
                         ResourceWarning, filename=__file__, lineno=13)
    multiprocessing = None
    CPU_CNT = 1
else:
    if os.name == 'posix' and 'SC_NPROCESSORS_CONF' in os.sysconf_names:
        CPU_CNT = os.sysconf('SC_NPROCESSORS_CONF')
    elif 'sched_getaffinity' in os.__all__:
        CPU_CNT = len(os.sched_getaffinity(0))  # pylint: disable=E1101
    else:
        CPU_CNT = os.cpu_count() or 1
finally:
    PROC_CNT = int(math.log2(CPU_CNT))


def getCurrentPool():
    """Return newly generated report names from the pool."""
    return getToBeProcessedFile()


def generateReport(pool, processes):
    """Write reports to /mad/report, and update database."""
    def call_func(func):
        return func()

    def load_file(path, default):
        if os.path.isfile(path):
            with open(path) as file:
                context = json.load(file)
        else:
            context = default
        return context

    def dump_file(path, context):
        with open(path, 'w') as file:
            json.dump(context, file, indent=2)

    print('Current worker pool:')
    pprint.pprint(pool)

    # original file content
    server_map = load_file('/mad/report/server_map.json', list())
    infected_computer = load_file('/mad/report/infected_computer.json', list())
    active_software = load_file('/mad/report/active_software.json', list())
    connection = load_file('/mad/report/connection.json', dict(nodes=list(), links=list()))

    # traverse report files
    for reportPath in pool:
        # load reports list
        with open(reportPath) as file:
            reportList = json.load(file)

        # make partial functions
        funcServerMap = functools.partial(updateServerMap,
                                          reportList=reportList,
                                          serverMap=server_map)
        funcInfectedComputer = functools.partial(updateInfectedComputer,
                                                 Report=reportList,
                                                 Infected=infected_computer)
        funcActiveSoftware = functools.partial(updateActiveSoftware,
                                               Report=reportList,
                                               Active=active_software)
        funcConnection = functools.partial(updateConnection,
                                           Report=reportList,
                                           Connection=connection)

        # run update process
        if processes <= 1:
            proc_return = [call_func(func) for func in [funcServerMap, funcInfectedComputer,
                                                        funcActiveSoftware, funcConnection]]
        else:
            proc_return = multiprocessing.Pool(processes).map(call_func, [funcServerMap, funcInfectedComputer,
                                                                          funcActiveSoftware, funcConnection])
        server_map, infected_computer, active_software, connection, loss = proc_return

        print(f'Generated report files for {reportPath!r}...')
        deleteToBeProcessedFile(reportPath)

    # save file content
    dump_file('/mad/report/server_map.json', server_map)
    dump_file('/mad/report/infected_computer.json', infected_computer)
    dump_file('/mad/report/active_software.json', active_software)
    dump_file('/mad/report/connection.json', connection)

    # get loss
    lossList = getLoss()
    loss = updateLoss(Report=lossList)
    dump_file('/mad/report/loss.json', loss)


def main():
    # default interval
    interval = 300
    process = PROC_CNT
    token = None

    # parse CLI
    opts, _ = getopt.getopt(sys.argv[1:], 'i:p:t:', ['interval=', 'process=', 'token='])
    for key, val in opts:
        if key in ('-i', '--interval'):
            interval = int(val)
        elif key in ('-p', '--process'):
            process = int(val)
        elif key in ('-t', '--token'):
            token = val
        else:
            sys.exit(f'usage: {sys.argv[0]} [-i SEC] [-p NUM] [-t KEY]')

    # setup environ
    if token is None:
        sys.exit(f'usage: {sys.argv[0]} [-i SEC] [-p NUM] [-t KEY]\n'
                 'mad_gen: error: argument KEY: no valid API token found')
    os.environ['MAD_TOKEN'] = token

    # check resource
    if multiprocessing is None:
        process = 0
    elif process > CPU_CNT:
        warnings.showwarning(f'current system has only {CPU_CNT} CPU'
                             f'{"s" if CPU_CNT > 1 else ""}; '
                             f'recommended process number is {PROC_CNT}',
                             ResourceWarning, filename=__file__, lineno=0,
                             line=f'{sys.executable} {" ".join(sys.argv)}')

    print('Runtime summary:')
    print()
    print(f'    System CPU count: {CPU_CNT}')
    print(f'    Concurrent process: {PROC_CNT}')
    print(f'    Sleep interval: {interval} second(s)')
    print(f'    API token: {token}')
    print()

    # update database
    updateToBeProcessedFile()
    while True:
        pool = getCurrentPool()
        if pool:
            generateReport(pool, PROC_CNT)
        else:
            print(f'No report in the pool, wait for another {interval} second(s).')
        time.sleep(interval)


if __name__ == '__main__':
    sys.exit(main())
