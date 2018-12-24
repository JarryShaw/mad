import os
import json
import time as _time
import random
import ast
from user_agents import parse as _parse


with open(os.path.join("./Background_PC", "index.json"), 'r') as f:
    index = json.load(f)
NUM = len(index)
STEP = 1209600/NUM
START = int(_time.mktime(_time.strptime('2018-07-11 0:0:0', "%Y-%m-%d %H:%M:%S")))


def parse(ua):
    info = _parse(ua)

    _list = str(info).split(' / ')

    _type = list()
    if info.is_mobile:
        _type.append('Mobile')
    if info.is_tablet:
        _type.append('Tablet')
    if info.is_touch_capable:
        _type.append('Touch Capable')
    if info.is_pc:
        _type.append('PC')
    if info.is_bot:
        _type.append('Bot')

    _dict = dict(
        device=_list[0],
        os=_list[1],
        browser=_list[2],
        type=' / '.join(_type) or 'Other',
    )
    __import__('pprint').pprint(_dict) ###
    return _dict


def readReportList(path):
    with open(os.path.join(path, "index.json"), 'r') as f:
        index = json.load(f)
        index.sort()
    return index


def writeInfected(index):
    Exist = list()
    Infected = list()
    infected = 0
    for count, file in enumerate(index):
        # infected = 0
        tmp_data = json.load(open("/usr/local/mad" + file, 'r'))
        # time = file.split('.')[0]
        # time = time.split('/')[-1]
        time = _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime(START+count*STEP))
        for i in tmp_data:
            # if not i['detected_by_cnn']:
            #     continue
            if i['is_malicious'] and i['srcIP'] not in Exist:
                infected += 1
                Exist.append(i['srcIP'])
        Infected.append({
            "time": time,
            "infected": infected
        })
    with open("infected_computer.json", 'w') as f:
        json.dump(Infected, f)


def writeActive(index):
    Active = list()
    for count, file in enumerate(index):
        tmp_data = json.load(open("/usr/local/mad" + file, 'r'))
        # time = file.split('.')[0]
        # time = time.split('/')[-1]
        time = _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime(START + count * STEP))
        benign = 0
        malicious = 0
        for i in tmp_data:
            # if not i['detected_by_cnn']:
            #     continue
            if i['is_malicious']:
                malicious += 1
            else:
                benign += 1
        Active.append({
            "time": time,
            "benign": benign,
            "malicious": malicious*50
        })
    with open("active_software.json", 'w') as f:
        json.dump(Active, f)


def writeConnection(index):
    Connection = {
        "nodes": [],
        "links": []
    }
    for file in index:
        tmp_data = json.load(open("/usr/local/mad" + file, 'r'))
        for i in tmp_data:
            # if not i['detected_by_cnn']:
            #     continue
            src = i['srcIP']
            dst = i['dstIP']
            if i['is_malicious']:
                flag = True
                flag1 = True
                flag2 = True
                for link in Connection["links"]:
                    if link["source"] == src and link["target"] == dst:
                        link["value"] += 1
                        flag = False
                for node in Connection["nodes"]:
                    if node["name"] == src:
                        flag1 = False
                        node["symbolSize"] = node["symbolSize"] + 0.1 if node["symbolSize"] < 20 else 20
                    if node["name"] == dst:
                        flag2 = False
                        node["symbolSize"] = node["symbolSize"] + 0.1 if node["symbolSize"] < 20 else 20
                if flag:
                    Connection["links"].append({
                        "source": src,
                        "target": dst,
                        "value": 1
                    })
                if flag1:
                    Connection["nodes"].append({
                        "name": src,
                        "category": 0,
                        "symbolSize": 10,
                        "draggable": "true"
                    })
                if flag2:
                    Connection["nodes"].append({
                        "name": dst,
                        "category": 1,
                        "symbolSize": 10,
                        "draggable": "true"
                    })
    with open("connection.json", 'w') as f:
        json.dump(Connection, f)


def writeUA(index):
    UA = list()
    for count, file in enumerate(index):
        tmp_data = json.load(open("/usr/local/mad" + file, 'r'))
        for i in tmp_data:
            # if not i['detected_by_cnn']:
            #     continue
            try:
                name = ast.literal_eval(f"""b'{i['UA']}'""").decode()
            except UnicodeDecodeError:
                name = i["UA"]
            type = i['is_malicious']
            # time = i['time']
            time = _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime(START + count * STEP + random.random() * STEP))
            info = parse(name)
            src = i['srcIP']
            dst = i['dstIP']
            url = i.get('malicious_url', [i['url']])
            detected_by_cnn = i['detected_by_cnn']
            if type:
                flag = True
                for j in UA:
                    if name == j['name'] and type == j['type']:
                        flag = False
                        if time < j['stime']:
                            j['stime'] = time
                        elif time > j['etime']:
                            j['etime'] = time
                        flag1 = True
                        for k in j['connections']:
                            if src == k['src'] and dst == k['dst']:
                                if time < k['stime']:
                                    k['stime'] = time
                                elif time > k['etime']:
                                    k['etime'] = time
                                flag1 = False
                                k["connection"].append({
                                    "time": time,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                })
                        if flag1:
                            j['connections'].append({
                                "src": src,
                                "dst": dst,
                                "stime": time,
                                "etime": time,
                                "connection": [{
                                    "time": time,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                }]
                            })
                        break
                if flag:
                    UA.append({
                        "name": name,
                        "type": type,
                        "stime": time,
                        "etime": time,
                        "info": info,
                        "connections": [{
                            "src": src,
                            "dst": dst,
                            "stime": time,
                            "etime": time,
                            "connection": [{
                                "time": time,
                                "url": url,
                                "detected_by_cnn": detected_by_cnn
                            }]
                        }]
                    })
    with open("UA.json", 'w') as f:
        json.dump(UA, f)


def writeInnerIP(index):
    innerIP = list()
    for count, file in enumerate(index):
        tmp_data = json.load(open("/usr/local/mad" + file, 'r'))
        for i in tmp_data:
            # if not i['detected_by_cnn']:
            #     continue
            try:
                name = ast.literal_eval(f"""b'{i['UA']}'""").decode()
            except UnicodeDecodeError:
                name = i["UA"]
            type = i['is_malicious']
            # time = i['time']
            time = _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime(START + count * STEP + random.random() * STEP))
            info = parse(name)
            src = i['srcIP']
            url = i.get('malicious_url', [i['url']])
            detected_by_cnn = i['detected_by_cnn']
            if type:
                flag = True
                for j in innerIP:
                    if src == j['IP']:
                        flag = False
                        flag2 = True
                        for k in j['UA']:
                            if name == k['name'] and type == k['type']:
                                flag2 = False
                                if time < k['stime']:
                                    k['stime'] = time
                                elif time > k['etime']:
                                    k['etime'] = time
                                k["connection"].append({
                                    "time": time,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                })
                        if flag2:
                            j["total"] += 1
                            if type == 1:
                                j["malicious"] += 1
                            j['UA'].append({
                                "name": name,
                                "stime": time,
                                "etime": time,
                                "type": type,
                                "info": info,
                                "connection": [{
                                    "time": time,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                }]
                            })
                        break
                if flag:
                    innerIP.append({
                        "IP": src,
                        "total": 1,
                        "malicious": type,
                        "UA": [
                            {
                                "name": name,
                                "stime": time,
                                "etime": time,
                                "type": type,
                                "info": info,
                                "connection": [{
                                    "time": time,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                }]
                            }
                        ]
                    })
    with open("innerIP.json", 'w') as f:
        json.dump(innerIP, f)


def writeOuterIP(index):
    outerIP = list()
    for count, file in enumerate(index):
        tmp_data = json.load(open("/usr/local/mad" + file, 'r'))
        for i in tmp_data:
            # if not i['detected_by_cnn']:
            #     continue
            try:
                name = ast.literal_eval(f"""b'{i['UA']}'""").decode()
            except UnicodeDecodeError:
                name = i["UA"]
            type = i['is_malicious']
            # time = i['time']
            time = _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime(START + count * STEP + random.random() * STEP))
            src = i['srcIP']
            dst = i['dstIP']
            url = i.get('malicious_url', [i['url']])
            detected_by_cnn = i['detected_by_cnn']
            if type:
                flag = True
                for j in outerIP:
                    if dst == j['IP']:
                        flag = False
                        if time < j['stime']:
                            j['stime'] = time
                        elif time > j['etime']:
                            j['etime'] = time
                        flag2 = True
                        for k in j['inner']:
                            if src == k['IP'] and name == k['UA']:
                                if time < k['stime']:
                                    k['stime'] = time
                                elif time > k['etime']:
                                    k['etime'] = time
                                k['connection'].append({
                                    "time": time,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                })
                                flag2 = False
                                break
                        if flag2:
                            j['inner'].append({
                                "IP": src,
                                "UA": name,
                                "stime": time,
                                "etime": time,
                                "connection": [{
                                    "time": time,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                }]
                            })
                        break
                if flag:
                    outerIP.append({
                        "IP": dst,
                        "type": type,
                        "stime": time,
                        "etime": time,
                        "inner": [{
                            "IP": src,
                            "UA": name,
                            "stime": time,
                            "etime": time,
                            "connection": [{
                                "time": time,
                                "url": url,
                                "detected_by_cnn": detected_by_cnn
                            }]
                        }]
                    })
    with open("outerIP.json", 'w') as f:
        json.dump(outerIP, f)


def writeExport(index):
    Export = list()
    for count, file in enumerate(index):
        tmp_data = json.load(open("/usr/local/mad" + file, 'r'))
        for i in tmp_data:
            # if not i['detected_by_cnn']:
            #     continue
            if i['is_malicious']:
                try:
                    name = ast.literal_eval(f"""b'{i['UA']}'""").decode()
                except UnicodeDecodeError:
                    name = i["UA"]
                time = _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime(START + count * STEP + random.random() * STEP))
                src = i['srcIP']
                dst = i['dstIP']
                srcPort = i['srcPort']
                dstPort = i['dstPort']
                Export.append({
                    "time": time,
                    "srcIP": src,
                    "dstIP": dst,
                    "srcPort": srcPort,
                    "dstPort": dstPort,
                    "UA": name
                })
    with open("export.json", 'w') as f:
        json.dump(Export, f)


def writeAll(index):
    infected = 0
    Exist = list()
    Infected = list()
    Active = list()
    Connection = {
        "nodes": [],
        "links": []
    }
    UA = list()
    innerIP = list()
    outerIP = list()
    Export = list()
    for count, file in enumerate(index):
        benign = 0
        malicious = 0
        tmp_data = json.load(open("/usr/local/mad" + file, 'r'))
        time_frame = _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime(START + count * STEP))
        for i in tmp_data:
            is_malicious = i['is_malicious']
            try:
                name = ast.literal_eval(f"""b'{i['UA']}'""").decode()
            except UnicodeDecodeError:
                name = i["UA"]
            info = i['info']
            src = i['srcIP']
            dst = i['dstIP']
            url = i.get('malicious_url', [i['url']])
            detected_by_cnn = i['detected_by_cnn']
            time_flow = _time.strftime("%Y-%m-%d %H:%M:%S", _time.localtime(START + count * STEP + random.random() * STEP))
            if is_malicious:
                srcPort = i['srcPort']
                dstPort = i['dstPort']
                Export.append({
                    "time": time_flow,
                    "srcIP": src,
                    "dstIP": dst,
                    "srcPort": srcPort,
                    "dstPort": dstPort,
                    "UA": name
                })
                malicious += 1
                if src not in Exist:
                    infected += 1
                    Exist.append(src)
                flag_haslink = True
                flag_hassrc = True
                flag_hasdst = True
                flag_hasUA = True
                flag_hasinner = True
                flag_hasouter = True
                for j in outerIP:
                    if dst == j['IP']:
                        flag_hasouter = False
                        if time_flow < j['stime']:
                            j['stime'] = time_flow
                        elif time_flow > j['etime']:
                            j['etime'] = time_flow
                        flag_outerhasconnection = True
                        for k in j['inner']:
                            if src == k['IP'] and name == k['UA']:
                                if time_flow < k['stime']:
                                    k['stime'] = time_flow
                                elif time_flow > k['etime']:
                                    k['etime'] = time_flow
                                k['connection'].append({
                                    "time": time_flow,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                })
                                flag_outerhasconnection = False
                                break
                        if flag_outerhasconnection:
                            j['inner'].append({
                                "IP": src,
                                "UA": name,
                                "stime": time_flow,
                                "etime": time_flow,
                                "connection": [{
                                    "time": time_flow,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                }]
                            })
                        break
                if flag_hasouter:
                    outerIP.append({
                        "IP": dst,
                        "type": is_malicious,
                        "stime": time_flow,
                        "etime": time_flow,
                        "inner": [{
                            "IP": src,
                            "UA": name,
                            "stime": time_flow,
                            "etime": time_flow,
                            "connection": [{
                                "time": time_flow,
                                "url": url,
                                "detected_by_cnn": detected_by_cnn
                            }]
                        }]
                    })
                for j in innerIP:
                    if src == j['IP']:
                        flag_hasinner = False
                        flag_innerhasUA = True
                        for k in j['UA']:
                            if name == k['name'] and is_malicious == k['type']:
                                flag_innerhasUA = False
                                if time_flow < k['stime']:
                                    k['stime'] = time_flow
                                elif time_flow > k['etime']:
                                    k['etime'] = time_flow
                                k["connection"].append({
                                    "time": time_flow,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                })
                        if flag_innerhasUA:
                            j["total"] += 1
                            if is_malicious == 1:
                                j["malicious"] += 1
                            j['UA'].append({
                                "name": name,
                                "stime": time_flow,
                                "etime": time_flow,
                                "type": is_malicious,
                                "info": info,
                                "connection": [{
                                    "time": time_flow,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                }]
                            })
                        break
                if flag_hasinner:
                    innerIP.append({
                        "IP": src,
                        "total": 1,
                        "malicious": is_malicious,
                        "UA": [
                            {
                                "name": name,
                                "stime": time_flow,
                                "etime": time_flow,
                                "type": is_malicious,
                                "info": info,
                                "connection": [{
                                    "time": time_flow,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                }]
                            }
                        ]
                    })
                for j in UA:
                    if name == j['name'] and is_malicious == j['type'] and dst == j['dst']:
                        flag_hasUA = False
                        if time_flow < j['stime']:
                            j['stime'] = time_flow
                        elif time_flow > j['etime']:
                            j['etime'] = time_flow
                        flag_UAhasconnection = True
                        for k in j['connections']:
                            if src == k['src']:
                                if time_flow < k['stime']:
                                    k['stime'] = time_flow
                                elif time_flow > k['etime']:
                                    k['etime'] = time_flow
                                    flag_UAhasconnection = False
                                k["connection"].append({
                                    "time": time_flow,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                })
                        if flag_UAhasconnection:
                            j['connections'].append({
                                "src": src,
                                "stime": time_flow,
                                "etime": time_flow,
                                "connection": [{
                                    "time": time_flow,
                                    "url": url,
                                    "detected_by_cnn": detected_by_cnn
                                }]
                            })
                        break
                if flag_hasUA:
                    UA.append({
                        "name": name,
                        "type": is_malicious,
                        "stime": time_flow,
                        "etime": time_flow,
                        "dst": dst,
                        "info": info,
                        "connections": [{
                            "src": src,
                            "stime": time_flow,
                            "etime": time_flow,
                            "connection": [{
                                "time": time_flow,
                                "url": url,
                                "detected_by_cnn": detected_by_cnn
                            }]
                        }]
                    })
                for link in Connection["links"]:
                    if link["source"] == src and link["target"] == dst:
                        link["value"] += 1
                        flag_haslink = False
                for node in Connection["nodes"]:
                    if node["name"] == src:
                        flag_hassrc = False
                        node["symbolSize"] = node["symbolSize"] + 0.1 if node["symbolSize"] < 20 else 20
                    if node["name"] == dst:
                        flag_hasdst = False
                        node["symbolSize"] = node["symbolSize"] + 0.1 if node["symbolSize"] < 20 else 20
                if flag_haslink:
                    Connection["links"].append({
                        "source": src,
                        "target": dst,
                        "value": 1
                    })
                if flag_hassrc:
                    Connection["nodes"].append({
                        "name": src,
                        "category": 0,
                        "symbolSize": 10,
                        "draggable": "true"
                    })
                if flag_hasdst:
                    Connection["nodes"].append({
                        "name": dst,
                        "category": 1,
                        "symbolSize": 10,
                        "draggable": "true"
                    })
            else:
                benign += 1
        Infected.append({
            "time": time_frame,
            "infected": infected
        })
        Active.append({
            "time": time_frame,
            "benign": benign,
            "malicious": malicious*50
        })
    with open("infected_computer.json", 'w') as f:
        json.dump(Infected, f)
    with open("active_software.json", 'w') as f:
        json.dump(Active, f)
    with open("connection.json", 'w') as f:
        json.dump(Connection, f)
    with open("UA.json", 'w') as f:
        json.dump(UA, f)
    with open("innerIP.json", 'w') as f:
        json.dump(innerIP, f)
    with open("outerIP.json", 'w') as f:
        json.dump(outerIP, f)
    with open("export.json", 'w') as f:
        json.dump(Export, f)


if __name__ == "__main__":
    index = readReportList("./Background_PC")
    # writeInnerIP(index)
    # writeUA(index)
    # writeOuterIP(index)
    # writeInfected(index)
    # writeConnection(index)
    # writeActive(index)
    # writeExport(index)
    writeAll(index)
