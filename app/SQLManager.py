# -*- coding: utf-8 -*-

from peewee import (BooleanField, CharField, DateTimeField, IntegerField,
                    Model, MySQLDatabase, TextField)

db = MySQLDatabase(
    database='deepocean',
    host='localhost',
    port=3306,
    user='root',
    passwd='zft13917331612',
    charset='utf8'
)


class BaseModel(Model):
    class Meta:
        database = db


class Mad_Report(BaseModel):
    name = CharField()
    is_malicious = BooleanField()
    ua = TextField()
    url = TextField()
    srcip = CharField()
    srcport = IntegerField()
    dstip = CharField()
    dstport = IntegerField()
    time = DateTimeField()
    detected_by_cnn = BooleanField()
    device = CharField()
    os = CharField()
    browser = CharField()
    type = CharField()


def saveReport(report):
    tmp = Mad_Report(
        name=report['filename'],
        is_malicious=report['is_malicious'],
        ua=report['UA'],
        url=report['url'],
        srcip=report['srcIP'],
        srcport=report['srcPort'],
        dstip=report['dstIP'],
        dstport=report['dstPort'],
        time=report['time'],
        detected_by_cnn=report['detected_by_cnn'],
        device=report['info']['device'],
        os=report['info']['os'],
        browser=report['info']['browser'],
        type=report['info']['type']
    )
    return tmp.save()


def saveReports(reportList):
    for report in reportList:
        status = saveReport(report)
        print(f'saving report {report["filename"]} status {status}')
