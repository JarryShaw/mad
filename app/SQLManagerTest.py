from SQLManager import *
import os
import json

with open('/usr/local/mad/report/Background_PC/index.json', 'r') as f:
    fileList = json.load(f)
for file in fileList:
    with open('/usr/local/mad' + file, 'r') as f:
        report = json.load(f)
    saveReports(report)
