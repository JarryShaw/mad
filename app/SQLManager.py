# -*- coding: utf-8 -*-

import functools

from peewee import (BooleanField, CharField, DateTimeField, FloatField,
                    IntegerField, Model, MySQLDatabase, TextField, fn)

db = MySQLDatabase(
    database='deepocean',
    host='mad_db',
    port=3306,
    user='root',
    passwd='zft13917331612',
    charset='utf8'
)


@functools.total_ordering
class minstr:
    def __gt__(self, other):
        return False


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
    count = Mad_ProcessedFile.select().count()  # pylint: disable=E1120
    minimum = Mad_ProcessedFile.select(fn.MIN(Mad_ProcessedFile.id)).scalar()  # pylint: disable=E1120
    while count >= 600:
        Mad_ProcessedFile.delete().where(Mad_ProcessedFile.id == minimum).execute()
        minimum += 1
        count = Mad_ProcessedFile.select().count()  # pylint: disable=E1120
    tmp = Mad_ProcessedFile(
        name=file
    )
    tmp.save()


def getProcessedFile():
    file = Mad_ProcessedFile.select(Mad_ProcessedFile.name).where(Mad_ProcessedFile.id == Mad_ProcessedFile.select(fn.MAX(Mad_ProcessedFile.id)).scalar()).dicts()  # pylint: disable=E1120 # noqa
    try:
        return file[0]['name']
    except IndexError:
        return minstr()


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
