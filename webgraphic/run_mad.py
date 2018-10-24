#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import shutil

from mad import main

# main(mode=2, path='/home/ubuntu/httpdump/wanyong80.pcap000', file='./data.json')

# main(mode=2, path='/data/wanyong-httpdump/20180408/20180309/wanyong.pcap000', file='./data.json')

# main(mode=5, path='/home/ubuntu/httpdump/wanyong80.pcap000', file='./data.json')

# main(mode=5, file='./data.new.json')

# main(file='./data.json')

parser = argparse.ArgumentParser(prog='mad',
                                 description='Malicious Application Detector')
parser.add_argument('-m', '--mode', action='store', default=3, type=int, choices=[1, 2, 3, 4, 5],
                    help='runtime mode')
parser.add_argument('-i', '--iface', action='store', default='eth0', type=str,
                    help='network interface for sniffing (mode=1), c.f. scapy.all.sniff(iface)')
parser.add_argument('-p', '--path', action='store', type=str,
                    help='input file name or directory (mode=1/2)')
parser.add_argument('-f', '--file', action='store', type=str,
                    help='JSON file name with list of input file names (mode=3)')
parser.add_argument('-s', '--shell', action='store_true', help=argparse.SUPPRESS)

args = parser.parse_args()
if args.shell:
    shell = os.environ.get('SHELL', shutil.which('sh'))
    os.execlp(shell, shell, '-i')
main(mode=args.mode, path=args.path, file=args.file, iface=args.iface)
