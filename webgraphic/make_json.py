# -*- coding: utf-8 -*-

import json
import os

temp = list()
# temp.extend(map(lambda name: f'/data/wanyong-httpdump/20180408/20180309/{name}',
#                 filter(lambda name: '.pcap' in os.path.splitext(name)[1],
#                         sorted(os.listdir(f"/data/wanyong-httpdump/20180408/20180309")))))
# temp.extend(map(lambda name: f'/data/wanyong-httpdump/20180407/{name}',
#                 filter(lambda name: '.pcap' in os.path.splitext(name)[1],
#                         sorted(os.listdir(f"/data/wanyong-httpdump/20180407")))))
# temp.extend(map(lambda name: f'/data/wanyong-httpdump/20180408/{name}',
#                 filter(lambda name: '.pcap' in os.path.splitext(name)[1],
#                         sorted(os.listdir(f"/data/wanyong-httpdump/20180408")))))
temp.extend(map(lambda name: f'/home/ubuntu/baiwei-sniffer-pcap/{name}',
                filter(lambda name: '.cap' in os.path.splitext(name)[1],
                        sorted(os.listdir('/home/ubuntu/baiwei-sniffer-pcap')))))

with open('./data.new.json', 'w') as file:
    json.dump(temp, file)

import pprint
pprint.pprint(temp)
