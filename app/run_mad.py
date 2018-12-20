#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
import os
import sys
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))  # noqa
################################################################################

import argparse
import time

from mad import main


def get_parser():
    parser = argparse.ArgumentParser(prog='mad',
                                     description='Malicious Application Detector')
    parser.add_argument('-v', '--version', action='version', version=time.strftime(r'%Y.%m.%d:%s'))

    parser.add_argument('-m', '--mode', action='store', default=3, type=int, choices=[1, 2, 3, 4, 5],
                        help='runtime mode')
    parser.add_argument('-p', '--path', action='store', type=str,
                        help='input file name or directory (mode=1/2)')
    parser.add_argument('-s', '--sample', action='store', type=str,
                        help='sample (mode=2, 5)')
    parser.add_argument('-t', '--tty', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('-d', '--devel', action='store_true', help=argparse.SUPPRESS)

    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    if args.tty:
        shell = os.environ.get('SHELL', 'sh')
        os.execlp(shell, shell)
    os.environ['MAD_DEVEL'] = str(args.devel)
    sys.exit(main(mode=args.mode, path=args.path, sample=args.sample))
