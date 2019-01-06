#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
import os
import sys
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))  # noqa
################################################################################

import argparse
import contextlib
import math
import resource
import time

# get SHELL
SHELL = os.environ.get('SHELL', '/bin/sh')

# limit on CPU
if os.name == 'posix' and 'SC_NPROCESSORS_CONF' in os.sysconf_names:
    CPU_CNT = os.sysconf('SC_NPROCESSORS_CONF')
elif 'sched_getaffinity' in os.__all__:
    CPU_CNT = len(os.sched_getaffinity(0))  # pylint: disable=E1101
else:
    CPU_CNT = os.cpu_count() or 1
PROC_CNT = int(math.log2(CPU_CNT))

# limit on memory (memlock)
MEMLOCK_SOFT = MEMLOCK_HARD = resource.RLIM_INFINITY
with contextlib.suppress(AttributeError, ValueError):
    MEMLOCK_SOFT, MEMLOCK_HARD = resource.getrlimit(resource.RLIMIT_MEMLOCK)
    if MEMLOCK_SOFT == sys.maxsize:
        MEMLOCK_SOFT = resource.RLIM_INFINITY
    if MEMLOCK_HARD == sys.maxsize:
        MEMLOCK_HARD = resource.RLIM_INFINITY

# limit on memory (vmem)
VMEM_SOFT = VMEM_HARD = resource.RLIM_INFINITY
with contextlib.suppress(AttributeError, ValueError):
    VMEM_SOFT, VMEM_HARD = resource.getrlimit(resource.RLIMIT_VMEM)  # pylint: disable=E1101
    if VMEM_SOFT == sys.maxsize:
        VMEM_SOFT = resource.RLIM_INFINITY
    if VMEM_HARD == sys.maxsize:
        VMEM_HARD = resource.RLIM_INFINITY


def get_parser():
    parser = argparse.ArgumentParser(prog='mad',
                                     description='Malicious Application Detector')
    parser.add_argument('-V', '--version', action='version', version=time.strftime(r'%Y.%m.%d:%s'))

    general_group = parser.add_argument_group(title='general arguments')
    general_group.add_argument('-m', '--mode', action='store', default=3, type=int, choices=[1, 2, 3, 4, 5],
                               help='runtime mode')
    general_group.add_argument('-p', '--path', action='store', type=str, default='/mad/pcap', metavar='DIR',
                               help='input file name or directory (mode=1/2/3)')
    general_group.add_argument('-s', '--sample', action='store', type=str, metavar='FILE',
                               help='sample for model training (mode=2/5)')

    runtime_group = parser.add_argument_group(title='runtime arguments')
    runtime_group.add_argument('-c', '--process', action='store', default=PROC_CNT, type=int, metavar='PROC',
                               help=f'number of concurrent processes that may run (default is {PROC_CNT})')
    runtime_group.add_argument('-l', '--memlock', action='store', default=MEMLOCK_HARD, type=int, metavar='MEM',
                               help=('number of bytes of memory that may be locked into RAM '
                                     f'(default is {"infinity" if MEMLOCK_HARD == resource.RLIM_INFINITY else MEMLOCK_HARD})'))  # noqa
    runtime_group.add_argument('-v', '--vmem', action='store', default=VMEM_HARD, type=int, metavar='MEM',
                               help=('largest area of mapped memory which the process may occupy '
                                     f'(default is {"infinity" if VMEM_HARD == resource.RLIM_INFINITY else MEMLOCK_HARD})'))  # noqa

    develop_group = parser.add_argument_group(title='development arguments')
    develop_group.add_argument('-i', '--interactive', action='store_true',
                               help='enter interactive mode (running SHELL)')
    develop_group.add_argument('-e', '--shell', action='store', default=SHELL,
                               help=f'shell for interactive mode (default is {SHELL!r})')
    develop_group.add_argument('-d', '--devel', action='store_true',
                               help='run in develop mode (quit after first round)')

    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    if args.interactive:
        shell = args.shell
        os.execlp(shell, shell)

    with contextlib.suppress(AttributeError, ValueError):
        memlock_hard = args.memlock
        memlock_soft = memlock_hard // 2
        if memlock_hard >= sys.maxsize:
            hard = resource.RLIM_INFINITY
        if memlock_soft >= sys.maxsize:
            memlock_soft = resource.RLIM_INFINITY
        resource.setrlimit(resource.RLIMIT_MEMLOCK, (memlock_soft, memlock_hard))

    with contextlib.suppress(AttributeError, ValueError):
        vmem_hard = args.vmem
        vmem_soft = vmem_hard // 2
        if vmem_soft >= sys.maxsize:
            vmem_soft = resource.RLIM_INFINITY
        resource.setrlimit(resource.RLIMIT_VMEM, (vmem_soft, vmem_hard))  # pylint: disable=E1101

    os.environ['CPU_CNT'] = str(CPU_CNT)
    os.environ['PROC_CNT'] = str(args.process)

    os.environ['MAD_PATH'] = str(args.path)
    os.environ['MAD_DEVEL'] = str(args.devel)

    print('Runtime summary:')
    print()
    print(f'    System CPU count: {CPU_CNT}')
    print(f'    System VMEM limit: ({"infinity" if VMEM_SOFT == resource.RLIM_INFINITY else VMEM_SOFT}, '
          f'{"infinity" if VMEM_HARD == resource.RLIM_INFINITY else VMEM_HARD})')
    print(f'    System MEMLOCK limit: ({"infinity" if MEMLOCK_SOFT == resource.RLIM_INFINITY else MEMLOCK_SOFT}, '
          f'{"infinity" if MEMLOCK_HARD == resource.RLIM_INFINITY else MEMLOCK_HARD})')
    print()
    print(f'    Concurrent process: {PROC_CNT}')
    print(f'    Current VMEM limit: ({"infinity" if vmem_soft == resource.RLIM_INFINITY else vmem_soft}, '
          f'{"infinity" if vmem_hard == resource.RLIM_INFINITY else vmem_hard})')
    print(f'    Current MEMLOCK limit: ({"infinity" if memlock_soft == resource.RLIM_INFINITY else memlock_soft}, '
          f'{"infinity" if memlock_hard == resource.RLIM_INFINITY else memlock_hard})')

    from mad import main
    sys.exit(main(mode=args.mode, path=args.path, sample=args.sample))
