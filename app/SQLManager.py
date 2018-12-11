# -*- coding: utf-8 -*-

from peewee import (BooleanField, CharField, DateTimeField, IntegerField,
                    Model, MySQLDatabase, TextField, FloatField, fn)

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


class Mad_Loss(BaseModel):
    time = DateTimeField()
    loss = FloatField()


class Mad_ProcessedFile(BaseModel):
    name = CharField()


def saveLoss(loss, time):
    tmp = Mad_Loss(
        loss=loss,
        time=time
    )
    tmp.save()


def saveProcessedFile(file):
    count = Mad_Report.select().count()
    while count >= 600:
        Mad_Report.delete().where(Mad_Report.id == fn.MIN(Mad_Report.id)).execute()
        count = Mad_Report.select().count()
    tmp = Mad_ProcessedFile(
        name=file
    )
    tmp.save()


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
