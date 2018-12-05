#!/usr/bin/env python3
# -*- coding: utf-8 -*-

################################################################################
import os
import sys
sys.path.insert(0, os.path.realpath(os.path.dirname(__file__)))  # noqa
################################################################################

import argparse

from mad import main

parser = argparse.ArgumentParser(prog='mad',
                                 description='Malicious Application Detector')
parser.add_argument('-m', '--mode', action='store', default=3, type=int, choices=[1, 2, 3, 4, 5],
                    help='runtime mode')
parser.add_argument('-p', '--path', action='store', type=str,
                    help='input file name or directory (mode=1/2)')
# parser.add_argument('-i', '--iface', action='store', default='eth0', type=str,
#                     help='network interface for sniffing (mode=1), c.f. scapy.all.sniff(iface)')
# parser.add_argument('-p', '--path', action='store', type=str,
#                     help='input file name or directory (mode=1/2)')
# parser.add_argument('-f', '--file', action='store', type=str,
#                     help='JSON file name with list of input file names (mode=3)')
parser.add_argument('-t', '--tty', action='store_true', help=argparse.SUPPRESS)

args = parser.parse_args()
if args.tty:
    shell = os.environ.get('SHELL', 'sh')
    os.execlp(shell, shell)
main(mode=args.mode, path=args.path)
# main(mode=args.mode, path=args.path, file=args.file, iface=args.iface)
