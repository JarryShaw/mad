#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
import os
import sys

sys.warnoptions.append('default::ResourceWarning:__main__')  # noqa
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))  # noqa
################################################################################

import argparse
import contextlib
import math
import resource
import shutil
import time
import warnings

# get SHELL
SHELL = os.environ.get('SHELL', shutil.which('sh'))

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

# limit on memory (as)
AS_SOFT = AS_HARD = resource.RLIM_INFINITY
with contextlib.suppress(AttributeError, ValueError):
    AS_SOFT, AS_HARD = resource.getrlimit(resource.RLIMIT_AS)
    if AS_SOFT == sys.maxsize:
        AS_SOFT = resource.RLIM_INFINITY
    if AS_HARD == sys.maxsize:
        AS_HARD = resource.RLIM_INFINITY

# limit on memory (swap)
SWAP_SOFT = SWAP_HARD = resource.RLIM_INFINITY
with contextlib.suppress(AttributeError, ValueError):
    SWAP_SOFT, SWAP_HARD = resource.getrlimit(resource.RLIMIT_SWAP)  # pylint: disable=E1101
    if SWAP_SOFT == sys.maxsize:
        SWAP_SOFT = resource.RLIM_INFINITY
    if SWAP_HARD == sys.maxsize:
        SWAP_HARD = resource.RLIM_INFINITY


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
                               help='sample file(s) for model training (mode=2/5)')

    runtime_group = parser.add_argument_group(title='runtime arguments')
    runtime_group.add_argument('-n', '--no-validate', action='store_true',
                               help='do not run validate process after prediction (mode=3)')
    runtime_group.add_argument('-t', '--sampling-interval', action='store', type=int, default=0, metavar='INT',
                               help='sample every %%INT%% file(s) (mode=3; default is 0, i.e. sampling from all files)')

    resource_group = parser.add_argument_group(title='resource arguments')
    resource_group.add_argument('-c', '--process', action='store', default=PROC_CNT, type=int, metavar='PROC',
                                help=f'number of concurrent processes that may run (default is {PROC_CNT})')
    resource_group.add_argument('-l', '--memlock', action='store', default=MEMLOCK_HARD, type=int, metavar='MEM',
                                help=('number of bytes of memory that may be locked into RAM '
                                      f'(default is {"unlimited" if MEMLOCK_HARD == resource.RLIM_INFINITY else MEMLOCK_HARD})'))  # noqa
    resource_group.add_argument('-v', '--vmem', action='store', default=VMEM_HARD, type=int, metavar='MEM',
                                help=('largest area of mapped memory which the process may occupy '
                                      f'(default is {"unlimited" if VMEM_HARD == resource.RLIM_INFINITY else VMEM_HARD})'))  # noqa
    resource_group.add_argument('-a', '--address-space', action='store', default=AS_HARD, type=int, metavar='MEM',
                                help=('maximum area (in bytes) of address space which may be taken by the process '
                                      f'(default is {"unlimited" if AS_HARD == resource.RLIM_INFINITY else AS_HARD})'))  # noqa
    resource_group.add_argument('-w', '--swap', action='store', default=SWAP_HARD, type=int, metavar='MEM',
                                help=('maximum size (in bytes) of the swap space that '
                                      "may be reserved or used by all of this user id's processes "
                                      f'(default is {"unlimited" if SWAP_HARD == resource.RLIM_INFINITY else SWAP_HARD})'))  # noqa

    develop_group = parser.add_argument_group(title='development arguments')
    develop_group.add_argument('-d', '--devel', action='store_true',
                               help='run in develop mode (quit after first round)')
    develop_group.add_argument('-i', '--interactive', action='store_true',
                               help='enter interactive mode (running SHELL)')
    develop_group.add_argument('-e', '--shell', action='store', default=SHELL,
                               help=f'shell for interactive mode (default is {SHELL!r})')

    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    if args.interactive:
        shell = args.shell
        os.execlp(shell, shell)

    if args.sampling_interval < 0:
        warnings.showwarning(f'invalid sampling interval: {args.sampling_interval}; '
                             f'sampling from all files instead',
                             RuntimeWarning, filename=__file__, lineno=0,
                             line=f'{sys.executable} {" ".join(sys.argv)}')
        args.sampling_interval = 0

    if args.process < 0:
        warnings.showwarning(f'invalid process number: {args.process}; '
                             f'using default number {PROC_CNT} instead',
                             RuntimeWarning, filename=__file__, lineno=0,
                             line=f'{sys.executable} {" ".join(sys.argv)}')
    else:
        if args.process > CPU_CNT:
            warnings.showwarning(f'current system has only {CPU_CNT} CPU'
                                 f'{"s" if CPU_CNT > 1 else ""}; '
                                 f'recommended process number is {PROC_CNT}',
                                 ResourceWarning, filename=__file__, lineno=0,
                                 line=f'{sys.executable} {" ".join(sys.argv)}')
        PROC_CNT = args.process

    try:
        if args.memlock < 0:
            memlock_hard = resource.RLIM_INFINITY
        else:
            memlock_hard = args.memlock
        memlock_soft = memlock_hard // 2
        if memlock_hard >= sys.maxsize:
            hard = resource.RLIM_INFINITY
        if memlock_soft >= sys.maxsize:
            memlock_soft = resource.RLIM_INFINITY
        resource.setrlimit(resource.RLIMIT_MEMLOCK, (memlock_soft, memlock_hard))
    except (AttributeError, ValueError) as error:
        memlock_hard = MEMLOCK_HARD
        memlock_soft = MEMLOCK_SOFT
        warnings.showwarning(f'setting MEMLOCK limit failed with error message: {error.args[0]!r}',
                             ResourceWarning, filename=__file__, lineno=0,
                             line=f'{sys.executable} {" ".join(sys.argv)}')

    try:
        if args.vmem < 0:
            vmem_hard = resource.RLIM_INFINITY
        else:
            vmem_hard = args.vmem
        vmem_soft = vmem_hard // 2
        if vmem_soft >= sys.maxsize:
            vmem_soft = resource.RLIM_INFINITY
        resource.setrlimit(resource.RLIMIT_VMEM, (vmem_soft, vmem_hard))  # pylint: disable=E1101
    except (AttributeError, ValueError) as error:
        vmem_hard = VMEM_HARD
        vmem_soft = VMEM_SOFT
        warnings.showwarning(f'setting VMEM limit failed with error message: {error.args[0]!r}',
                             ResourceWarning, filename=__file__, lineno=0,
                             line=f'{sys.executable} {" ".join(sys.argv)}')

    try:
        if args.address_space < 0:
            as_hard = resource.RLIM_INFINITY
        else:
            as_hard = args.address_space
        as_soft = as_hard // 2
        if as_soft >= sys.maxsize:
            as_soft = resource.RLIM_INFINITY
        resource.setrlimit(resource.RLIMIT_AS, (as_soft, as_hard))
    except (AttributeError, ValueError) as error:
        as_hard = AS_HARD
        as_soft = AS_SOFT
        warnings.showwarning(f'setting AS limit failed with error message: {error.args[0]!r}',
                             ResourceWarning, filename=__file__, lineno=0,
                             line=f'{sys.executable} {" ".join(sys.argv)}')

    try:
        if args.swap < 0:
            swap_hard = resource.RLIM_INFINITY
        else:
            swap_hard = args.swap
        swap_soft = swap_hard // 2
        if swap_soft >= sys.maxsize:
            swap_soft = resource.RLIM_INFINITY
        resource.setrlimit(resource.RLIMIT_SWAP, (swap_soft, swap_hard))  # pylint: disable=E1101
    except (AttributeError, ValueError) as error:
        swap_hard = VMEM_HARD
        swap_soft = VMEM_SOFT
        warnings.showwarning(f'setting SWAP limit failed with error message: {error.args[0]!r}',
                             ResourceWarning, filename=__file__, lineno=0,
                             line=f'{sys.executable} {" ".join(sys.argv)}')

    os.environ['CPU_CNT'] = str(CPU_CNT)
    os.environ['PROC_CNT'] = str(PROC_CNT)

    os.environ['MAD_PATH'] = str(args.path)
    os.environ['MAD_DEVEL'] = str(args.devel)
    os.environ['MAD_NOVAL'] = str(args.no_validate)
    os.environ['MAD_INTERVAL'] = str(args.sampling_interval)

    print('Runtime summary:')
    print()
    print(f'    System CPU count: {CPU_CNT}')
    print(f'    System AS limit: ({"unlimited" if AS_SOFT == resource.RLIM_INFINITY else AS_SOFT}, '
          f'{"unlimited" if AS_HARD == resource.RLIM_INFINITY else AS_HARD})')
    print(f'    System SWAP limit: ({"unlimited" if SWAP_SOFT == resource.RLIM_INFINITY else SWAP_SOFT}, '
          f'{"unlimited" if SWAP_HARD == resource.RLIM_INFINITY else SWAP_HARD})')
    print(f'    System VMEM limit: ({"unlimited" if VMEM_SOFT == resource.RLIM_INFINITY else VMEM_SOFT}, '
          f'{"unlimited" if VMEM_HARD == resource.RLIM_INFINITY else VMEM_HARD})')
    print(f'    System MEMLOCK limit: ({"unlimited" if MEMLOCK_SOFT == resource.RLIM_INFINITY else MEMLOCK_SOFT}, '
          f'{"unlimited" if MEMLOCK_HARD == resource.RLIM_INFINITY else MEMLOCK_HARD})')
    print()
    print(f'    Concurrent process: {PROC_CNT}')
    print(f'    Concurrent AS limit: ({"unlimited" if as_soft == resource.RLIM_INFINITY else as_soft}, '
          f'{"unlimited" if as_hard == resource.RLIM_INFINITY else as_hard})')
    print(f'    Concurrent SWAP limit: ({"unlimited" if swap_soft == resource.RLIM_INFINITY else swap_soft}, '
          f'{"unlimited" if swap_hard == resource.RLIM_INFINITY else swap_hard})')
    print(f'    Concurrent VMEM limit: ({"unlimited" if vmem_soft == resource.RLIM_INFINITY else vmem_soft}, '
          f'{"unlimited" if vmem_hard == resource.RLIM_INFINITY else vmem_hard})')
    print(f'    Concurrent MEMLOCK limit: ({"unlimited" if memlock_soft == resource.RLIM_INFINITY else memlock_soft}, '
          f'{"unlimited" if memlock_hard == resource.RLIM_INFINITY else memlock_hard})')
    print()

    from mad import main
    sys.exit(main(mode=args.mode, path=args.path, sample=args.sample))
