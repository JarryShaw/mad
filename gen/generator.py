# -*- coding: utf-8 -*-


def updateInfectedComputer(Report, Infected):
    Exist = list()
    infected = 0
    time = Report[0]['time']
    for i in Report:
        if i['time'] < time:
            time = i['time']
        if i['is_malicious'] and i['srcIP'] not in Exist:
            infected += 1
            Exist.append(i['srcIP'])
    Infected.append({
        "time": time,
        "infected": infected
    })
    return Infected


def updateActiveSoftware(Report, Active):
    Exist = list()
    time = Report[0].time
    benign = 0
    malicious = 0
    for i in Report:
        if i['time'] < time:
            time = i['time']
        if i['ua'] in Exist:
            continue
        if i['is_malicious']:
            malicious += 1
            Exist.append(i['ua'])
        else:
            benign += 1
            Exist.append(i['ua'])
    Active.append({
        "time": time,
        "benign": benign,
        "malicious": malicious
    })
    return Active


def updateConnection(Report, Connection):
    for i in Report:
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
    return Connection


def updateLoss(Report):
    Loss = list()
    for i in Report:
        Loss.append({
            "time": i.time,
            "loss": i.loss
        })
    return Loss
