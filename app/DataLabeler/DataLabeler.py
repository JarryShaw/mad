# -*- coding: utf-8 -*-

from queue import Queue

from DataLabeler.VirusTotal3 import virustotal  # pylint: disable=E0401, E0611
from DataLabeler.VirusTotalThread import ViruTotalThread  # pylint: disable=E0401, E0611


class Datalabler:
    def __init__(self):
        self.scanner = virustotal()
        self.ThreadPool = []
        self.workQueue = Queue()
        self.resultQueue = Queue()
        self.ThreadNum = 10
        self.counter = counter(0)

    def setThreadNum(self, num):
        self.ThreadNum = num

    def lable(self, urls):
        for x in urls:
            self.workQueue.put(x)

        self.counter.set(len(urls))

        for _ in range(self.ThreadNum):
            tmp = ViruTotalThread(self.scanner, self.workQueue, self.resultQueue, self.counter)
            self.ThreadPool.append(tmp)

        for x in self.ThreadPool:
            x.start()

        for x in self.ThreadPool:
            x.join()

        print("所有url已经扫描完毕")
        result = []
        while not self.resultQueue.empty():
            result.append(self.resultQueue.get())

        self.ThreadPool = []

        return result


class counter:
    def __init__(self, num):
        self.total = num

    def set(self, num):
        self.total = num

    def __sub__(self, other):
        self.total -= other
        return self

    def __str__(self):
        return str(self.total)


if __name__ == "__main__":
    urls = []
    f = open("LableUrls.txt")
    line = f.readline()
    while line:
        line = line.strip("\n")
        urls.append(line)
        line = f.readline()
    f.close()
    print("共有", len(urls), "个url需要标记")
    labeler = Datalabler()
    labeler.setThreadNum(20)
    result = labeler.lable(urls)
    for x in result:
        print(x)
