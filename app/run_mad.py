#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
import os
import sys
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))  # noqa
################################################################################

import argparse
import contextlib
import resource
import time

if os.name == 'posix' and 'SC_NPROCESSORS_CONF' in os.sysconf_names:
    CPU_CNT = os.sysconf('SC_NPROCESSORS_CONF')
elif 'sched_getaffinity' in os.__all__:
    CPU_CNT = len(os.sched_getaffinity(0))  # pylint: disable=E1101
else:
    CPU_CNT = os.cpu_count() or 1


def get_parser():
    parser = argparse.ArgumentParser(prog='mad',
                                     description='Malicious Application Detector')
    parser.add_argument('-v', '--version', action='version', version=time.strftime(r'%Y.%m.%d:%s'))

    general_group = parser.add_argument_group(title='general arguments')
    general_group.add_argument('-m', '--mode', action='store', default=3, type=int, choices=[1, 2, 3, 4, 5],
                               help='runtime mode')
    general_group.add_argument('-p', '--path', action='store', type=str,
                               help='input file name or directory (mode=1/2/3)')
    general_group.add_argument('-s', '--sample', action='store', type=str,
                               help='sample (mode=2/5)')

    runtime_group = parser.add_argument_group(title='runtime arguments')
    runtime_group.add_argument('-c', '--cpu', action='store', default=CPU_CNT, type=int,
                               help='override the detection of CPUs on the machine (mode=3)')
    runtime_group.add_argument('-l', '--memory', action='store', default=(1 << 30), type=int,
                               help='number of bytes of memory that may be locked into RAM')

    develop_group = parser.add_argument_group(title='development arguments')
    develop_group.add_argument('-i', '--interactive', action='store_true',
                               help='enter interactive mode (running SHELL)')
    develop_group.add_argument('-e', '--shell', action='store', default=os.environ.get('SHELL', 'sh'),
                               help='shell for interactive mode')
    develop_group.add_argument('-d', '--devel', action='store_true',
                               help='run in develop mode (quit after first round)')

    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    if args.interactive:
        shell = args.shell
        os.execlp(shell, shell)

    with contextlib.suppress(AttributeError):
        soft = args.memory
        hard = resource.getrlimit(resource.RLIMIT_MEMLOCK)[1]
        if hard == sys.maxsize:
            hard = resource.RLIM_INFINITY
        resource.setrlimit(resource.RLIMIT_MEMLOCK, (soft, hard))

    with contextlib.suppress(AttributeError):
        soft = args.memory
        hard = resource.getrlimit(resource.RLIMIT_VMEM)[1]  # pylint: disable=E1101
        if hard == sys.maxsize:
            hard = resource.RLIM_INFINITY
        resource.setrlimit(resource.RLIMIT_VMEM, (soft, hard))  # pylint: disable=E1101

    os.environ['CPU_CNT'] = str(args.cpu)
    os.environ['MAD_DEVEL'] = str(args.devel)

    from mad import main
    sys.exit(main(mode=args.mode, path=args.path, sample=args.sample))
