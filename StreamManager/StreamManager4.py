import os
import re
from scapy.all import *
from DataLabeler.DataLabeler import Datalabler

class StreamManager:
    def __init__(self,pcapkit,sniffedPackets):
        self.pcapkit=pcapkit
        self.packets=sniffedPackets
        path=os.getcwd()

        self.backgroud_groups_PC={}
        self.backgroud_groups_Phone = {}
        self.suspicious_group={}

        self.backgroud_PC=[]
        self.backgroud_Phone = []
        self.suspicious=[]

    '''
    def generate(self):
        back=os.path.dirname(os.path.realpath(__file__))
        os.chdir(self.datapath)
        re=os.system("pkt2flow -xv -o ./tmp "+self.filename)
        print("执行命令")
        if re!=0:
            print("流转化失败！")
            return
        os.chdir("./tmp")
        os.system("mv tcp_nosyn/* ./")
        os.system("rm -r tcp_nosyn/")
        os.system("mv tcp_syn/* ./")
        os.system("rm -r tcp_syn/")
        os.chdir(back)
    '''
    def classify(self,ips):
        count_f=0
        count_no=0
        # info=self.pcapkit.trace()
        info=self.pcapkit
        total=len(info)
        for y in info:
            x=y["label"]
            ip=self.getIP(x)
            if ip in ips[-1] or ip in ips[0] or ip in ips[2]:
                print("过滤流:",x)
                count_f+=1
                continue
            if self.isLocalIP(ip[0]):
                dst_ip = ip[1]
                src_ip = ip[0]
            else:
                dst_ip = ip[0]
                src_ip = ip[1]
            #if ip in ips[0]:
             #   self.browser_PC.append({"label":x,"type":1,"is_malicious":0})
            if ip in ips[1]:
                self.backgroud_PC.append({"label":x,"index":y["index"],"UA":y["UA"],"internal_ip":src_ip,"external_ip":dst_ip,"type":1,"is_malicious":0})
            elif ip in ips[3]:
                self.backgroud_Phone.append({"label":x,"index":y["index"],"UA":y["UA"],"internal_ip":src_ip,"external_ip":dst_ip,"type":2,"is_malicious":0})
            elif ip in ips[4]:
                self.suspicious.append({"label":x,"index":y["index"],"UA":y["UA"],"internal_ip":src_ip,"external_ip":dst_ip,"type":3,"is_malicious":0})
            else:
                print("找不到",ip)
                count_no+=1

        print("共有:",total,"个文件")
        print("过滤了：",count_f,"个文件")
        print("找不到",count_no,"个文件")


        print("-----------------------------")
        print("PC软件：", self.backgroud_PC)
        print("-----------------------------")
        print("Phone软件：", self.backgroud_Phone)
        print("-----------------------------")
        print("无ua嫌疑软件：",self.suspicious)


    def Group(self):
        #labling
        '''
        print("开始标记数据")
        print("正在标记数据类型1...")
        self.lable(self.browser_PC)
        print("正在标记数据类型2...")
        self.lable(self.backgroud_PC)
        print("正在标记数据类型3...")
        self.lable(self.browser_Phone)
        print("正在标记数据类型4...")
        self.lable(self.backgroud_Phone)
        print("正在标记数据类型5...")
        self.lable(self.suspicious)
        print("数据标记完毕，开始聚类...")
        '''




        # backgroudtype PC
        for i in range(len(self.backgroud_PC)):
            UA = self.backgroud_PC[i]["UA"]
            ip = self.backgroud_PC[i]["external_ip"]
            key = ip + " " + UA
            if key in self.backgroud_groups_PC:
                self.backgroud_groups_PC[key].append(self.backgroud_PC[i])
            else:
                tmp = []
                tmp.append(self.backgroud_PC[i])
                self.backgroud_groups_PC[key] = list(tmp)

                # browsertype


        # backgroudtype PC
        for i in range(len(self.backgroud_Phone)):
            UA = self.backgroud_Phone[i]["UA"]
            ip = self.backgroud_Phone[i]["external_ip"]
            key = ip + " " + UA
            if key in self.backgroud_groups_Phone:
                self.backgroud_groups_Phone[key].append(self.backgroud_Phone[i])
            else:
                tmp = []
                tmp.append(self.backgroud_Phone[i])
                self.backgroud_groups_Phone[key] = list(tmp)

        # empty_ua
        for i in range(len(self.suspicious)):
            UA = self.suspicious[i]["UA"]
            ip = self.suspicious[i]["external_ip"]
            key = ip + " " + UA
            if key in self.suspicious_group:
                self.suspicious_group[key].append(self.suspicious[i])
            else:
                tmp = []
                tmp.append(self.suspicious[i])
                self.suspicious_group[key] = list(tmp)

        print("聚类处理完毕")
        print("种类1group数量：", len(self.backgroud_groups_PC))
        print("种类2group数量：", len(self.backgroud_groups_Phone))
        print("种类3group数量：", len(self.suspicious_group))
        # labling
        '''
        print("开始标记数据")
        print("正在标记数据类型1...")
        self.lable(self.browser_groups_PC)
        print("正在标记数据类型2...")
        self.lable(self.backgroud_groups_PC)
        print("正在标记数据类型3...")
        self.lable(self.browser_groups_Phone)
        print("正在标记数据类型4...")
        self.lable(self.backgroud_groups_Phone)
        print("正在标记数据类型5...")
        self.lable(self.suspicious_group)
       '''
        #validating

    def labelGroups(self):
        print("开始标记数据")
        print("正在标记数据类型1...")
        self.lable(self.backgroud_groups_PC)
        print("正在标记数据类型2...")
        self.lable(self.backgroud_groups_Phone)
        print("正在标记数据类型3...")
        self.lable(self.suspicious_group)

    def lable(self,target_groups):
        urls=[]
        keys=[]
        for key in target_groups:
            ip=target_groups[key][0]["external_ip"]
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
        l=Datalabler()
        l.setThreadNum(20)
        result = l.lable(urls)
        for x in result:
            url_tmp=x["url"]
            for i in range(len(urls)):
                if url_tmp == urls[i]:
                    for index in range(len(target_groups[keys[i]])):
                        target_groups[keys[i]][index]["is_malicious"]+=x["malicious"]
                        target_groups[keys[i]][index]["is_malicious"] +=x["suspicious"]
                        if x["malicious"]!=0 or x["suspicious"]!=0:
                            print("扫描命中！！！！")


    @staticmethod
    def validate(dict):
        targets=[]
        for key in dict:
            for x in dict[key]:
                if x["is_malicious"]>0:
                    targets.append(x)
        urls=[]
        index=[]

        malicious_num=0
        for i in range(len(targets)):
            index=targets[i]["index"]
            # url=self.GetUrl(index)
            url=re.sub("https://", "", targets[i]["url"])
            if url=="none":
                malicious_num+=1
            else:
                urls.append(url)
                index.append(i)

        if not urls:
            print("无内容需要验证")
            return []
        else:
            url_to_scan=list(set(urls))

        false_alarm=[]

        l = Datalabler()
        l.setThreadNum(20)
        result = l.lable(url_to_scan)
        for x in result:
            if x["malicious"]==0 and x["suspicious"]==0:
                url_tmp=x["url"]
                for i in range(len(urls)):
                    if url_tmp==urls[i]:
                        false_alarm.append(targets[index[i]]["label"])
            else:
                malicious_num+=1

        print("总共标记:",len(targets),"个恶意流")
        print("virustotal检测出的恶意流个数为:",malicious_num)

        return false_alarm

    def extractIP(self,ipUA):
        raw=ipUA.split()
        return raw[0]

    def GetDataForCNN(self):
        tmp=[]


        for key in self.backgroud_groups_PC:
            for x in self.backgroud_groups_PC[key]:
                tmp.append(x)




        for key in self.backgroud_groups_Phone:
            for x in self.backgroud_groups_Phone[key]:
                tmp.append(x)

        for key in self.suspicious_group:
            for x in self.suspicious_group[key]:
                tmp.append(x)

        return tmp



    def GetBackgroudGroup_PC(self):
        print(self.backgroud_groups_PC)
        return self.backgroud_groups_PC



    def GetBackgroudGroup_Phone(self):
        print(self.backgroud_groups_Phone)
        return self.backgroud_groups_Phone

    def GetSuspicious(self):
        print(self.suspicious_group)
        return self.suspicious_group

    def getIP(self,filename):
        tmp=filename.split("_")
        ip1=tmp[0]
        ip2=tmp[2]
        result=[]
        result.append(ip1)
        result.append(ip2)
        result.sort()
        return result

    def get_ip(self,label):
        tmp=label.split("-")
        raw1=tmp[0]
        raw2=tmp[1]
        s1=raw1.split("_")
        s2=raw2.split("_")
        ip1=""
        ip2=""
        for i in range(4):
            ip1+=s1[i]
            ip2+=s2[i]
            if i!=3:
                ip1+="."
                ip2+="."
        result=[]
        result.append(ip1)
        result.append(ip2)
        result.sort()
        return result

    def GetUrl(self, index):
        pattern1 = "/.*?HTTP"
        pattern2 = "/.*?\\?"
        pattern3 = "Host.*?\\\\r"

        uri_tmp = "none"
        for i in index:
            packet=self.packets[i]
            try:
                s = str(packet[Raw].load)
            except:
                continue
            ptr = ".*(GET|POST|HEAD).*HTTP.*"
            if re.match(ptr, s):
                ttt = re.findall(pattern1, s)[0]
                if not re.findall(pattern2, ttt):
                    ttt = ttt.strip(" HTTP")
                else:
                    ttt = re.findall(pattern2, ttt)[0].strip("?")
                try:
                    uri = re.findall(pattern3, s)[0].strip("\\r").strip("Host: ") + ttt
                except:
                    continue
                uri_tmp = re.sub("http://", "", uri)
                break

        return uri_tmp
    '''
    def getUA(self,filename):
        filepath = self.datapath + "/tmp/"+filename
        pattern="User-Agent.*?\\\\r"

        useragent="UnknownUA"

        source = PcapReader(filepath)
        packet = source.read_packet()
        while packet:
            try:
                s = str(packet[Raw].load)
            except:
                packet = source.read_packet()
                continue
            ptr=".*(GET|POST|HEAD).*HTTP.*"
            if re.match(ptr, s):
                try:
                    ua = re.findall(pattern,s)[0].strip("\\r")
                    ua=re.sub("User-Agent: ","",ua)
                    useragent=ua
                except:
                    packet = source.read_packet()
                    continue
                break
            packet = source.read_packet()
        return useragent
    '''
    '''
    def GetUrl(self,filename):
        filepath=self.datapath+"/tmp/"+filename
        pattern1= "/.*?HTTP"
        pattern2="/.*?\\?"
        pattern3="Host.*?\\\\r"

        source = PcapReader(filepath)
        packet = source.read_packet()
        uri_tmp="none"
        while packet:
            try:
                s = str(packet[Raw].load)
            except:
                packet = source.read_packet()
                continue
            ptr = ".*(GET|POST|HEAD).*HTTP.*"
            if re.match(ptr, s):
                ttt = re.findall(pattern1, s)[0]
                if not re.findall(pattern2, ttt):
                    ttt = ttt.strip(" HTTP")
                else:
                    ttt = re.findall(pattern2, ttt)[0].strip("?")
                try:
                    uri = re.findall(pattern3, s)[0].strip("\\r").strip("Host: ") + ttt
                except:
                    packet = source.read_packet()
                    continue
                uri_tmp=re.sub("http://","",uri)
                break
            else:
                packet = source.read_packet()

        return uri_tmp
    '''
    def isLocalIP(self,IP):
        local=["10\\..*","192\\.168\\..*","172\\.16\\..*","172\\.17\\..*","172\\.18\\..*","172\\.19\\..*"
            , "172\\.20\\..*","172\\.21\\..*","172\\.22\\..*","172\\.23\\..*","172\\.24\\..*","172\\.25\\..*"
            , "172\\.26\\..*","172\\.27\\..*","172\\.28\\..*","172\\.29\\..*","172\\.30\\..*","172\\.31\\..*"]
        for x in local:
            if re.match(x,IP):
                return True
        return False
