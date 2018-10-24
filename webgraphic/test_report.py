# -*- coding: utf-8 -*-


import datetime
import ipaddress
import json
import random

from useragents.useragents import parse


MAX_IP = 0xffff_ffff_ffff_ffff_ffff_ffff_ffff_ffff
MAX_PORT = 0xffff

report = list()
useragents = parse()
useragent_names = list(useragents.keys()) + ['UnknownUA']

for _ in range(100):
    srcip = str(ipaddress.ip_address(random.randint(0, MAX_IP)))
    dstip = str(ipaddress.ip_address(random.randint(0, MAX_IP)))
    srcport = random.randint(0, MAX_PORT)
    dstport = random.randint(0, MAX_PORT)
    timestamp = datetime.datetime.now().isoformat()
    ua = random.choice(useragent_names)
    report.append(dict(
        srcIP=srcip,
        srcPort=srcport,
        dstIP=dstip,
        dstPort=dstport,
        time=timestamp,
        name=f'{srcip}_{srcport}-{dstip}_{dstport}-{timestamp}',
        UA=ua,
        info=useragents.get(ua,
                dict(desc=None, type=None, comment=None, link=(None, None))),
    ))

with open('test_report.json', 'w') as file:
    json.dump(report, file)
