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
    name = CharField(max_length=255)
    is_malicious = BooleanField()
    ua = TextField()
    url = TextField()
    srcip = CharField(max_length=255)
    srcport = IntegerField()
    dstip = CharField(max_length=255)
    dstport = IntegerField()
    time = DateTimeField()
    detected_by_cnn = BooleanField()
    device = CharField(max_length=255)
    os = CharField(max_length=255)
    browser = CharField(max_length=255)
    type = CharField(max_length=255)


class Mad_Loss(BaseModel):
    time = DateTimeField()
    loss = FloatField()


class Mad_ProcessedFile(BaseModel):
    name = CharField(max_length=255)
