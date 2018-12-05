# -*- coding: utf-8 -*-

import json
import os

from SQLManager import saveReports

if __name__ == '__main__':
    with open('/usr/local/mad/report/Background_PC/index.json', 'r') as f:
        fileList = json.load(f)
    for file in fileList:
        with open('/usr/local/mad' + file, 'r') as f:
            report = json.load(f)
        saveReports(report)
