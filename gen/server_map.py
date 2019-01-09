# -*- coding: utf-8 -*-

import copy
import ipaddress
import json
import os
import time

import requests

API_KEY = os.environ['MAD_TOKEN']


def updateServerMap(reportList, serverMap):
    # backup server_map
    server_map = copy.copy(serverMap)

    # load failed IP addresses
    if os.path.isfile('/mad/failed.json'):
        with open('mad/failed.json') as file:
            failed = set(json.load(file))
    else:
        failed = set()

    # get IP addresses pool
    ip_list = list()
    for report in filter(lambda r: r['is_malicious'], reportList):
        ip = report['dstip']
        if ipaddress.ip_address(ip).is_private:
            continue
        ip_list.append(ip)
    ip_pool = set(ip_list) - failed - set(map(lambda d: d['name'], serverMap))

    # fetch IP addresses information
    for ip in ip_pool:
        request = requests.get(f'https://api.shodan.io/shodan/host/{ip}?key={API_KEY}')
        print(ip, request.status_code)
        if request.ok:
            context = request.json()
            latitude = context['latitude']
            longitude = context['longitude']
            server_map.append(dict(
                name=ip,
                latLng=[latitude, longitude],
            ))
        else:
            failed.add(ip)
        time.sleep(1)

    # return modified server_map
    return server_map
