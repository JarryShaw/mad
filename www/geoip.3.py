# -*- coding: utf-8 -*-


import copy
import ipaddress
import json
# import os

import geocoder
import requests


TOKEN = 'a5b4675abed361'

# with open('/usr/local/mad/report/Background_PC/index.json') as file:
#     filelist = json.load(file)

# ipset = list()
# for filename in sorted(filelist):
#     # print(f'/usr/loca/mad{filename}') ###
#     with open(f'/usr/local/mad{filename}') as file:
#         report = json.load(file)
#     for item in report:
#         if not item['is_malicious']:    continue
#         ipset.append(item['dstIP'])

ipset = ['1.9.56.8', '101.199.103.206', '101.227.0.138', '101.227.0.140', '101.227.102.196', '101.227.102.208', '101.227.160.28', '101.227.175.215', '101.227.176.38', '101.227.200.136', '101.227.209.211', '101.227.209.212', '101.227.209.213', '101.227.209.214', '101.227.209.215', '101.227.209.218', '101.227.209.233', '101.227.209.234', '101.227.216.141', '101.227.216.142', '101.227.216.145', '101.227.216.146', '101.227.216.147', '101.227.216.148', '101.227.216.150', '101.227.216.159', '101.227.216.160', '101.227.22.157', '101.227.22.158', '101.227.22.159', '101.227.22.160', '101.227.22.161', '101.227.97.163', '101.227.97.184', '101.227.98.121', '103.228.71.185', '106.15.83.5', '106.38.219.49', '106.75.20.51', '106.75.26.22', '106.75.60.77', '111.230.214.130', '112.65.74.130', '112.74.124.230', '114.236.141.11', '114.236.141.21', '114.236.92.129', '114.55.188.99', '114.80.177.122', '114.80.177.123', '114.80.177.99', '114.80.182.156', '115.239.211.112', '115.28.254.87', '115.29.247.141', '116.224.86.46', '116.224.87.43', '116.230.143.103', '116.62.32.197', '118.178.232.169', '118.24.79.244', '118.31.164.92', '118.89.208.235', '118.89.214.208', '120.55.82.128', '120.92.32.209', '120.92.32.253', '120.92.33.171', '121.201.12.239', '121.248.150.193', '122.205.110.5', '122.225.28.135', '122.225.67.225', '122.225.81.60', '122.226.182.68', '122.226.62.1', '122.227.201.86', '122.228.72.158', '123.125.29.147', '123.151.39.158', '123.151.39.159', '123.151.65.30', '123.206.4.74', '123.59.68.172', '124.112.127.76', '125.78.252.37', '14.215.140.21', '150.138.238.148', '172.16.100.13', '175.102.131.51', '175.102.131.56', '175.102.131.57', '175.102.131.58', '175.102.131.63', '175.102.131.71', '175.102.131.83', '180.101.150.25', '180.101.150.26', '180.101.150.27', '180.101.150.28', '180.101.150.29', '180.101.150.30', '180.101.150.31', '180.101.150.32', '180.101.153.40', '180.101.217.189', '180.101.57.129', '180.153.100.146', '180.153.100.191', '180.153.100.193', '180.153.105.151', '180.153.105.156', '180.153.105.158', '180.153.105.160', '180.153.105.161', '180.153.105.162', '180.153.105.164', '180.153.105.167', '180.153.105.168', '180.153.129.140', '180.153.222.195', '180.153.93.49', '180.153.93.79', '180.163.155.5', '180.163.155.8', '180.163.155.9', '180.163.159.9', '180.163.159.95', '180.163.198.47', '180.163.198.48', '180.163.251.240', '180.163.251.247', '180.163.255.156', '180.163.68.29', '180.235.71.94', '180.96.0.140', '180.96.69.20', '180.96.69.26', '180.97.176.149', '180.97.196.46', '180.97.8.120', '182.254.10.50', '182.254.116.117', '182.254.93.101', '182.61.62.41', '182.84.120.1', '182.92.29.97', '183.131.124.89', '183.134.53.218', '183.136.215.1', '183.61.106.141', '183.61.38.230', '192.168.254.7', '192.168.56.181', '192.3.185.51', '202.85.212.166', '213.32.69.77', '218.242.131.167', '220.181.172.34', '221.228.219.105', '222.184.110.1', '222.186.137.234', '222.186.137.235', '222.186.137.242', '222.186.172.129', '222.73.132.141', '222.73.132.143', '222.73.132.144', '222.73.132.145', '222.73.132.146', '222.73.132.147', '222.73.132.149', '222.73.132.152', '222.73.132.153', '222.73.132.154', '222.73.132.155', '222.73.132.156', '222.73.132.157', '222.73.132.158', '222.73.132.159', '222.73.132.160', '222.73.61.234', '223.202.200.189', '223.26.106.20', '23.59.139.27', '36.110.220.15', '36.110.236.223', '36.152.3.105', '36.152.3.11', '36.152.3.114', '36.27.210.59', '42.62.49.216', '47.89.42.160', '47.92.21.16', '47.92.5.193', '47.93.160.174', '47.93.76.169', '47.93.77.222', '47.93.77.62', '52.80.140.204', '54.223.129.71', '58.215.118.48', '58.216.107.194', '58.216.6.154', '58.218.203.138', '58.218.203.226', '58.218.203.230', '58.218.203.231', '58.218.203.246', '58.220.38.193', '58.220.43.41', '58.220.68.1', '58.222.32.1', '58.223.165.200', '58.83.229.22', '59.110.149.175', '59.110.149.177', '59.78.84.123', '60.205.86.200', '60.205.93.93', '61.129.7.20', '61.147.122.129', '61.147.234.78', '61.147.234.79', '61.155.170.129', '61.155.201.38', '61.155.201.96', '74.208.105.171']

with open('webPage/server_map.json') as file:
    geoip = json.load(file)

with open('/usr/local/mad/report/server_map.json', 'w') as file:
        json.dump(geoip, file)

resip = list()
for count, ip in enumerate(ipset[166:]):
    if ipaddress.ip_address(ip).is_private:
        print(count+167, ip, 'private address')
        continue
    latlng = geocoder.ip(ip).latlng
    # try:
    #     r = requests.get(f'http://ipinfo.io/{ip}?token={TOKEN}')
    #     j = r.json()['loc']
    #     l = j.split(',')
    #     latlng = (float(l[0]), float(l[1]))
    # except requests.exceptions.ConnectionError:
    #     latlng = None
    print(count+167, ip, latlng) ###
    if latlng:
        geoip.append(dict(
            name=ip,
            latLng=latlng,
        ))
    if latlng is None:
        resip.append((ip, 0))

with open('/usr/local/mad/report/server_map.json', 'w') as file:
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
