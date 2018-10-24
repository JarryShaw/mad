# -*- coding: utf-8 -*-


import json
import os
import pathlib
import shutil

from StreamManager.StreamManager4 import *


# data = list()
# data.extend(map(lambda name: f'/data/wanyong-httpdump/20180408/20180309/{name}',
#                 filter(lambda name: '.pcap' in os.path.splitext(name)[1],
#                         sorted(os.listdir(f"/data/wanyong-httpdump/20180408/20180309")))))
# data.extend(map(lambda name: f'/data/wanyong-httpdump/20180407/{name}',
#                 filter(lambda name: '.pcap' in os.path.splitext(name)[1],
#                         sorted(os.listdir(f"/data/wanyong-httpdump/20180407")))))
# data.extend(map(lambda name: f'/data/wanyong-httpdump/20180408/{name}',
#                 filter(lambda name: '.pcap' in os.path.splitext(name)[1],
#                         sorted(os.listdir(f"/data/wanyong-httpdump/20180408")))))

with open('data.json') as file:
    data = json.load(file)

with open('/usr/local/mad/report/index.json.0') as file:
    index = json.load(file)

for count, filename in enumerate(sorted(index)):
    # if filename > '2018-07-24T01:58:12.321071.json':    break

    with open(filename) as file:
        report = json.load(file)

    path = f'/usr/local/mad/dataset/{pathlib.Path(filename).stem}'
    stream = StreamManager(data[count], path)
    stream.generate()

    group_dict = {'Background_PC': []}
    for item in report:
        if item['detected_by_cnn']:     continue
        if not item['is_malicious']:    continue
        group_dict['Background_PC'].append(dict(
            is_malicious=1,
            type=item['type'],
            filename=item['filename'],
        ))

    val, url = stream.validate(group_dict)
    for item in report:
        if item['detected_by_cnn']:     continue
        if not item['is_malicious']:    continue
        flag = int(item['filename'] in val)
        if flag:
            ind = val.index(item['filename'])
            item['malicious_url'] = url[ind]
        else:
            item['malicious_url'] = None

    with open(filename, 'w') as file:
        json.dump(report, filename)

    shutil.rmtree(f'{path}/stream')
