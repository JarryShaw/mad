#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getopt
import math
import os
import sys
import time
import warnings
import json
import ast
from SQLManager import getToBeProcessedFile

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


def generateReport(reportPath):
    """Write reports to /mad/report, and update database."""
    pass


def main():
    # default interval
    interval = 300
    process = PROC_CNT

    # parse CLI
    opts, _ = getopt.getopt(sys.argv[1:], 'i:p:', ['interval=', 'process='])
    for key, val in opts:
        if key in ('-i', "--interval"):
            interval = int(val)
        elif key in ('-p', '--process'):
            process = int(val)
        else:
            sys.exit(f'usage: {sys.argv[0]} [-i SEC] [-p PROC]')

    # check resource
    if multiprocessing is None:
        process = 0
    elif process > CPU_CNT:
        warnings.showwarning(f'current system has only {CPU_CNT} CPU'
                             f'{"s" if CPU_CNT > 1 else ""}; '
                             f'recommended process number is {PROC_CNT}',
                             ResourceWarning, filename=__file__, lineno=0,
                             line=f'{sys.executable} {" ".join(sys.argv)}')

    # update database
    while True:
        pool = getCurrentPool()
        if pool:
            if process <= 1:
                [generateReport(file) for file in pool]
            else:
                multiprocessing.Pool(processes=process).map(generateReport, pool)
        else:
            print(f'No report in the pool, wait for another {interval} seconds.')
        time.sleep(interval)


if __name__ == '__main__':
    sys.exit(main())
