#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import time

from multiprocessing import Process


class Paths:

    capture = "/home/bro/capture"
    schedule = "/home/bro/capture/bro.txt"


def extract(path):
    print("process %s" % path)
    command = [
        "bro",
        "-r",
        path,
        "/home/bro/scripts/plugins/extract-pe.bro"
    ]
    os.system(" ".join(command))


def init():
    if not os.path.exists(Paths.schedule):
        with open(Paths.schedule, "wb") as fp:
            pass


def main():
    init()
    finished = []
    with open(Paths.schedule, "rb") as fp:
        for line in fp:
            finished.append(line.strip())
    while True:
        pcaps = []
        for i in os.listdir(Paths.capture):
            if i.endswith(".pcap"):
                pcaps.append(i)
        pcaps.sort()
        pcaps.pop()
        todo = []
        for p in pcaps:
            if p in finished:
                # print("skip %s" % p)
                continue
            todo.append(p)
            if len(todo) == 5:
                break
        processes = [
            Process(
                target=extract,
                args=(os.path.join(Paths.capture, p), )
            )
            for p in todo
        ]
        for p in processes:
            p.start()
        for p in processes:
            p.join()
        for p in todo:
            finished.append(p)
            with open(Paths.schedule, "ab") as fp:
                fp.write(p + "\n")
        time.sleep(10)


if __name__ == '__main__':
    main()
