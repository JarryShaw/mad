# -*- coding: utf-8 -*-
from peewee import *


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
    us = CharField()
    url = CharField()
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
