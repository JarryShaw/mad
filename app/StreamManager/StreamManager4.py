# -*- coding: utf-8 -*-

import ast
import ipaddress
import os
import pathlib
import random
import re
import subprocess

import dpkt

from DataLabeler.DataLabeler import Datalabler  # pylint: disable=E0401

# devel flag
DEVEL = ast.literal_eval(os.environ['MAD_DEVEL'])


class StreamManager:
    def __init__(self, filename, datapath):
        # self.filename=filename
        # path=os.getcwd()
        # self.datapath=path+"/stream/"+filename.strip('.pcap')
        # root, file = os.path.split(filename)
        self.filename = filename
        self.datapath = datapath
        self.background_groups_PC = {}
        self.background_groups_Phone = {}
        self.suspicious_group = {}
        self.background_PC = []
        self.background_Phone = []
        self.suspicious = []

    def generate(self):
        # back=os.path.dirname(os.path.realpath(__file__))
        # os.chdir(self.datapath)
        # re=os.system("pkt2flow -xv -o ./tmp "+self.filename)
        # print("执行命令")
        # if re!=0:
        #     print("流转化失败！")
        #     return
        # os.chdir("./tmp")
        # os.system("mv tcp_nosyn/* ./")
        # os.system("rm -r tcp_nosyn/")
        # os.system("mv tcp_syn/* ./")
        # os.system("rm -r tcp_syn/")
        # os.chdir(back)
        pathlib.Path(f"{self.datapath}/stream").mkdir(parents=True, exist_ok=True)
        cmd = ['pkt2flow', '-xv', '-o', f'{self.datapath}/tmp', self.filename]
        try:
            print(f"执行命令：{' '.join(cmd)!r}")
            subprocess.check_call(cmd)
        except subprocess.CalledProcessError:
            # if subp.returncode != 0:
            print("流转化失败！")
            # return
            raise
        print("流转化完成！")
        # with contextlib.suppress(OSError):
        #     for entry in filter(lambda e: e.is_file(), os.scandir(f'{self.datapath}/tmp/tcp_nosyn')):
        #         if DEVEL:
        #             shutil.copy(entry.path, f'{self.datapath}/stream/{entry.name}')
        #         else:
        #             os.rename(entry.path, f'{self.datapath}/stream/{entry.name}')
        # with contextlib.suppress(OSError):
        #     for entry in filter(lambda e: e.is_file(), os.scandir(f'{self.datapath}/tmp/tcp_syn')):
        #         if DEVEL:
        #             shutil.copy(entry.path, f'{self.datapath}/stream/{entry.name}')
        #         else:
        #             os.rename(entry.path, f'{self.datapath}/stream/{entry.name}')
        verb = 'ln' if DEVEL else 'mv'
        # file_list = glob.glob(f'{self.datapath}/tmp/*/*.pcap')
        # for file in file_list:
        #     cmd = f'{verb} -f {file} {self.datapath}/stream/'
        #     print(f"执行命令：{cmd!r}")
        #     os.system(cmd)
        try:
            cmd = f'find {self.datapath}/tmp -name "*.pcap" -print0 | xargs -0 {verb} -fvt {self.datapath}/stream/'
            print(f"执行命令：{cmd!r}")
            subprocess.check_call(cmd, shell=True)
        except subprocess.CalledProcessError:
            print("流转移失败！")
            raise
        print("流转移完成！")

    def classify(self, ips):
        files = os.listdir(self.datapath+"/stream")
        count_f = 0
        count_no = 0
        total = len(files)
        for x in files:
            ip = self.getIP(x)
            if ip in ips[-1] or ip in ips[0] or ip in ips[2]:
                # print("过滤流文件:",x)
                # print(len(files))
                count_f += 1
                continue
            if ip in ips[1]:
                self.background_PC.append({"filename": x, "type": 2, "is_malicious": 0, "http": [], "UA": 0, "url": 0})
            elif ip in ips[3]:
                self.background_Phone.append(
                    {"filename": x, "type": 4, "is_malicious": 0, "http": [], "UA": 0, "url": 0})
            elif ip in ips[4]:
                self.suspicious.append({"filename": x, "type": 5, "is_malicious": 0, "http": [], "UA": 0, "url": 0})
            else:
                # print("找不到",ip)
                count_no += 1

        print("共有:", total, "个文件")
        print("过滤了：", count_f, "个文件")
        print("找不到", count_no, "个文件")

        print("-----------------------------")
        print("PC软件：", self.background_PC)
        print("-----------------------------")
        print("Phone软件：", self.background_Phone)
        print("-----------------------------")
        print("无ua嫌疑软件：", self.suspicious)

    def Group(self):
        # labling
        '''
        print("开始标记数据")
        print("正在标记数据类型1...")
        self.lable(self.browser_PC)
        print("正在标记数据类型2...")
        self.lable(self.background_PC)
        print("正在标记数据类型3...")
        self.lable(self.browser_Phone)
        print("正在标记数据类型4...")
        self.lable(self.background_Phone)
        print("正在标记数据类型5...")
        self.lable(self.suspicious)
        print("数据标记完毕，开始聚类...")
        '''

        print("正在成组数据类型2...")
        # backgroundtype PC
        for i in range(len(self.background_PC)):
            UA, url, http_load = self.getUA(self.background_PC[i]["filename"])
            ip = self.getIP(self.background_PC[i]["filename"])
            tag = ip[0]
            if self.isLocalIP(ip[0]):
                tag = ip[1]
            key = tag + " " + UA
            self.background_PC[i]["http"] = http_load
            self.background_PC[i]["url"] = url
            self.background_PC[i]["UA"] = UA
            if key in self.background_groups_PC:
                self.background_groups_PC[key].append(self.background_PC[i])
            else:
                tmp = []
                tmp.append(self.background_PC[i])
                self.background_groups_PC[key] = list(tmp)

                # browsertype

        print("正在成组数据类型4...")
        # backgroundtype PC
        for i in range(len(self.background_Phone)):
            UA, url, http_load = self.getUA(self.background_Phone[i]["filename"])
            ip = self.getIP(self.background_Phone[i]["filename"])
            tag = ip[0]
            if self.isLocalIP(ip[0]):
                tag = ip[1]
            key = tag + " " + UA
            self.background_Phone[i]["http"] = http_load
            self.background_Phone[i]["url"] = url
            self.background_Phone[i]["UA"] = UA
            if key in self.background_groups_Phone:
                self.background_groups_Phone[key].append(self.background_Phone[i])
            else:
                tmp = []
                tmp.append(self.background_Phone[i])
                self.background_groups_Phone[key] = list(tmp)

        print("正在成组数据类型5...")
        # empty_ua
        for i in range(len(self.suspicious)):
            UA, url, http_load = self.getUA(self.suspicious[i]["filename"])
            ip = self.getIP(self.suspicious[i]["filename"])
            tag = ip[0]
            if self.isLocalIP(ip[0]):
                tag = ip[1]
            key = tag + " "+UA
            self.suspicious[i]["http"] = http_load
            self.suspicious[i]["url"] = url
            self.suspicious[i]["UA"] = UA
            if key in self.suspicious_group:
                self.suspicious_group[key].append(self.suspicious[i])
            else:
                tmp = []
                tmp.append(self.suspicious[i])
                self.suspicious_group[key] = list(tmp)

        print("聚类处理完毕")
        print("种类2group数量：", len(self.background_groups_PC))
        print("种类4group数量：", len(self.background_groups_Phone))
        print("种类5group数量：", len(self.suspicious_group))
        # labling
        '''
        print("开始标记数据")
        print("正在标记数据类型1...")
        self.lable(self.browser_groups_PC)
        print("正在标记数据类型2...")
        self.lable(self.background_groups_PC)
        print("正在标记数据类型3...")
        self.lable(self.browser_groups_Phone)
        print("正在标记数据类型4...")
        self.lable(self.background_groups_Phone)
        print("正在标记数据类型5...")
        self.lable(self.suspicious_group)
       '''
        # validating

    def labelGroups(self):
        print("开始标记数据")
        print("正在标记数据类型2...")
        self.lable(self.background_groups_PC)
        print("正在标记数据类型4...")
        self.lable(self.background_groups_Phone)
        print("正在标记数据类型5...")
        self.lable(self.suspicious_group)

    def lable(self, target_groups):
        urls = []
        keys = []
        for key in target_groups:
            ip = self.extractIP(key)
            urls.append(ip)
            keys.append(key)
        print(urls)

        '''
        urls_tolable=[]
        for i in urls:
            for j in i:
                urls_tolable.append(j)
        '''
        if not urls:
            print("无内容需要标记")
            return
        ll = Datalabler()
        ll.setThreadNum(20)
        result = ll.lable(urls)
        for x in result:
            url_tmp = x["url"]
            for i in range(len(urls)):
                if url_tmp == urls[i]:
                    for index in range(len(target_groups[keys[i]])):
                        target_groups[keys[i]][index]["is_malicious"] += x["malicious"]
                        target_groups[keys[i]][index]["is_malicious"] += x["suspicious"]
                        if x["malicious"] != 0 or x["suspicious"] != 0:
                            print("扫描命中！！！！")

    def validate(self, dict):
        targets = []
        for key in dict:
            for x in dict[key]:
                if x["is_malicious"] > 0:
                    targets.append(x)
        urls = []
        index = []

        malicious_num = 0
        for i in range(len(targets)):
            filename = targets[i]["filename"]
            url = self.GetUrls(filename)
            if len(url) == 0:
                malicious_num += 1
            else:
                urls.append(url)
                index.append(i)

        if not urls:
            print("无内容需要验证")
            return [], []
        else:
            urls_temp = []
            for x in urls:
                for y in x:
                    urls_temp.append(y)
            url_to_scan = list(set(urls_temp))

        true_alarm = []
        true_malicious_urls = []

        ll = Datalabler()
        ll.setThreadNum(20)
        result = ll.lable(url_to_scan)
        for x in result:
            if x["state"] == 0:
                url_tmp = x["url"]
                for i in range(len(urls)):
                    if url_tmp in urls[i]:
                        filename = targets[index[i]]["filename"]
                if filename not in true_alarm:
                    if random.randint(1, 1000) == 151:
                        true_alarm.append(filename)
                        true_malicious_urls.append(url_tmp)
                continue
            if x["malicious"] >= 1 or x["suspicious"] >= 1:
                url_tmp = x["url"]
                for i in range(len(urls)):
                    if url_tmp in urls[i]:
                        filename = targets[index[i]]["filename"]
                        if filename not in true_alarm:
                            true_alarm.append(targets[index[i]]["filename"])
                            true_malicious_urls.append(url_tmp)
            else:
                malicious_num += 1

        print("总共标记:", len(targets), "个恶意流")
        print("virustotal检测出的误报恶意流个数为:", malicious_num)

        return true_alarm, true_malicious_urls

    def extractIP(self, ipUA):
        raw = ipUA.split()
        return raw[0]

    def GetDataForCNN(self):
        tmp = []

        for key in self.background_groups_PC:
            for x in self.background_groups_PC[key]:
                tmp.append(x)

        for key in self.background_groups_Phone:
            for x in self.background_groups_Phone[key]:
                tmp.append(x)

        for key in self.suspicious_group:
            for x in self.suspicious_group[key]:
                tmp.append(x)

        return tmp

    def GetBackgroundGroup_PC(self):
        # print(self.background_groups_PC)
        return self.background_groups_PC

    def GetBackgroundGroup_Phone(self):
        # print(self.background_groups_Phone)
        return self.background_groups_Phone

    def GetSuspicious(self):
        # print(self.suspicious_group)
        return self.suspicious_group

    def getIP(self, filename):
        tmp = filename.split("_")
        ip1 = tmp[0]
        ip2 = tmp[2]
        result = []
        result.append(ip1)
        result.append(ip2)
        result.sort()
        return result

    def getUA(self, filename):
        filepath = self.datapath + "/stream/"+filename
        pattern = "User-Agent.*?\\\\r"
        pattern1 = "/.*?HTTP"
        pattern2 = "/.*?\\?"
        pattern3 = "Host.*?\\\\r"

        useragent = "UnknownUA"
        uri_tmp = "none"

        f = open(filepath, "rb")
        source = dpkt.pcap.Reader(f)
        packet = dpkt_next(source)
        http_load = []
        got_ua = 0
        got_uri = 0
        while packet:
            # s = packet_to_bytes(packet)
            payload = packet_to_bytes(packet)
            s = str(payload, encoding='utf-8', errors='replace')
            '''
            try:
                s = str(packet[Raw].load)
            except Exception:
                packet = source.read_packet()
                continue
            '''
            ptr = ".*(GET|POST|HEAD).*HTTP.*"
            if re.match(ptr, s):
                http_load.append(payload)
                # s = s.decode()
                if not got_ua:
                    try:
                        ua = re.findall(pattern, s)[0].strip("\\r")
                        ua = re.sub("User-Agent: ", "", ua)
                        useragent = ua
                        got_ua = 1
                    except Exception:
                        pass
                if not got_uri:
                    try:
                        ttt = re.findall(pattern1, s)[0]
                    except Exception:
                        ttt = ""
                    if not re.findall(pattern2, ttt):
                        ttt = ttt.strip(" HTTP")
                    else:
                        ttt = re.findall(pattern2, ttt)[0].strip("?")
                    try:
                        uri = re.findall(pattern3, s)[0].strip("\\r").strip("Host: ") + ttt
                        uri_tmp = re.sub("http://", "", uri)
                        got_uri = 1
                    except Exception:
                        pass
            packet = dpkt_next(source)
        f.close()
        return useragent, uri_tmp, http_load

    def GetUrl(self, filename):
        filepath = self.datapath+"/stream/"+filename
        pattern1 = "/.*?HTTP"
        pattern2 = "/.*?\\?"
        pattern3 = "Host.*?\\\\r"

        f = open(filepath, "rb")
        source = dpkt.pcap.Reader(f)
        packet = dpkt_next(source)
        uri_tmp = "none"
        while packet:
            s = packet_to_str(packet)
            ptr = ".*(GET|POST|HEAD).*HTTP.*"
            if re.match(ptr, s):
                try:
                    ttt = re.findall(pattern1, s)[0]
                except Exception:
                    ttt = ""
                if not re.findall(pattern2, ttt):
                    ttt = ttt.strip(" HTTP")
                else:
                    ttt = re.findall(pattern2, ttt)[0].strip("?")
                try:
                    uri = re.findall(pattern3, s)[0].strip("\\r").strip("Host: ") + ttt
                    uri_tmp = re.sub("http://", "", uri)
                except Exception:
                    packet = dpkt_next(source)
                    continue
                break
            packet = dpkt_next(source)
        f.close()
        return uri_tmp

    def GetUrls(self, filename):
        filepath = self.datapath+"/stream/"+filename
        pattern1 = "/.*?HTTP"
        pattern2 = "/.*?\\?"
        pattern3 = "Host.*?\\\\r"

        f = open(filepath, "rb")
        source = dpkt.pcap.Reader(f)
        packet = dpkt_next(source)
        uri_tmp = []
        while packet:
            s = packet_to_str(packet)
            ptr = ".*(GET|POST|HEAD).*HTTP.*"
            if re.match(ptr, s):
                try:
                    ttt = re.findall(pattern1, s)[0]
                except Exception:
                    ttt = ""
                if not re.findall(pattern2, ttt):
                    ttt = ttt.strip(" HTTP")
                else:
                    ttt = re.findall(pattern2, ttt)[0].strip("?")
                try:
                    uri = re.findall(pattern3, s)[0].strip("\\r").strip("Host: ") + ttt
                    uri_tmp.append(re.sub("http://", "", uri))
                except Exception:
                    packet = dpkt_next(source)
                    continue
            packet = dpkt_next(source)
        f.close()
        return uri_tmp

    def isLocalIP(self, IP):
        # local = ["10\\..*", "192\\.168\\..*", "172\\.16\\..*", "172\\.17\\..*", "172\\.18\\..*", "172\\.19\\..*", "172\\.20\\..*", "172\\.21\\..*", "172\\.22\\..*",  # noqa
        #          "172\\.23\\..*", "172\\.24\\..*", "172\\.25\\..*", "172\\.26\\..*", "172\\.27\\..*", "172\\.28\\..*", "172\\.29\\..*", "172\\.30\\..*", "172\\.31\\..*"]  # noqa
        # for x in local:
        #     if re.match(x, IP):
        #         return True
        # return False
        return ipaddress.ip_address(IP).is_private


def dpkt_next(reader):
    try:
        p = next(reader)
        return p
    except Exception:
        return None


def packet_to_str(packet):
    try:
        p = dpkt.ethernet.Ethernet(packet[1])
        s = str(p.data.data.pack()[p.data.data.__hdr_len__:])
    except Exception:
        return "notvalid"
    return s


def packet_to_bytes(packet):
    try:
        p = dpkt.ethernet.Ethernet(packet[1])
        s = p.data.data.pack()[p.data.data.__hdr_len__:]
    except Exception:
        return b"notvalid"
    return s
