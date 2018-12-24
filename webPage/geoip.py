# -*- coding: utf-8 -*-


import copy
import ipaddress
import json
import os

import geocoder
import requests


TOKEN = 'a5b4675abed361'

with open('/usr/local/mad/report/Background_PC/index.json') as file:
    filelist = json.load(file)

ipset = list()
for filename in sorted(filelist):
    # print(f'/usr/loca/mad{filename}') ###
    with open(f'/usr/local/mad{filename}') as file:
        report = json.load(file)
    for item in report:
        if not item['is_malicious']:    continue
        ipset.append(item['dstIP'])

resip = list()
geoip = list()
for count, ip in enumerate(sorted(set(ipset))):
    if ipaddress.ip_address(ip).is_private:
        print(count+1, ip, 'private address')
        continue
    latlng = geocoder.ip(ip).latlng
    # try:
    #     r = requests.get(f'http://ipinfo.io/{ip}?token={TOKEN}')
    #     j = r.json()['loc']
    #     l = j.split(',')
    #     latlng = (float(l[0]), float(l[1]))
    # except requests.exceptions.ConnectionError:
    #     latlng = None
    print(count+1, ip, latlng) ###
    if latlng:
        geoip.append(dict(
            name=ip,
            latLng=latlng,
        ))
    if latlng is None:
        resip.append((ip, 0))

with open('server_map.json', 'w') as file:
    json.dump(geoip, file)

while resip:
    temp = copy.deepcopy(resip)
    resip = list()
    for ip, count in temp:
        if count > 100:
            print('failed', ip, count)
        count += 1
        latlng = geocoder.ip(ip).latlng
        # try:
        #     r = requests.get(f'http://ipinfo.io/{ip}?token={TOKEN}')
        #     j = r.json()['loc']
        #     l = j.split(',')
        #     latlng = (float(l[0]), float(l[1]))
        # except requests.exceptions.ConnectionError:
        #     latlng = None
        print('retry', ip, latlng) ###
        if latlng:
            geoip.append(dict(
                name=ip,
                latLng=latlng,
            ))
        if latlng is None:
            resip.append((ip, count))

    with open('/usr/local/mad/report/server_map.json', 'w') as file:
        json.dump(geoip, file)

with open('/usr/local/mad/report/server_map.json', 'w') as file:
    json.dump(geoip, file)
