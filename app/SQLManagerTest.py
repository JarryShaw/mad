from SQLManager import *
import os
import json


fileList = os.scandir('/usr/local/mad/report/Background_PC/')
for file in fileList:
    with open(file.path, 'r') as f:
        report = json.load(f)
    saveReport(report)
