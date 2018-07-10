import requests
import random
import time
import os
from urllib import parse
class virustotal:
    def __init__(self):
        self.agents=[
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]
        self.ip=[]
        path=os.getcwd()
        f=open("/home/ubuntu/MaliciousApplicationDetector/DataLabeler/proxies3.txt","rb")
        line=f.readline()
        count=0
        while line:
            count+=1
            raw=line.split()
            self.ip.append(raw[1].decode("gb2312")+":"+raw[2].decode("gb2312"))
            line=f.readline()
            if line:
                line=f.readline()
        print("初始化完成，共有：",count,"个可用代理")
        f.close()

    def label(self,url):
        data=self.PostAndScan(url)
        if not data:
            print("扫描失败")
            return False
        result=self.GetReport(data)
        if not result:
            print("扫描失败")
            return False
        return result

    def PostAndScan(self,url):
        dict={"url":url}
        u=parse.urlencode(dict)
        u = "https://www.virustotal.com/ui/urls?"+u
        retry_time=0
        while retry_time<100:
            agent=self.GetAgent()
            ip=self.GetIP()
            proxies={"https":ip}
            print("正在扫描：",u,"使用ip代理：",ip,"  使用UA：",agent)
            try:
                response = requests.post(u, headers={
                    #"User-Agent": agent,
                    "Referer": "https://www.virustotal.com/"},proxies=proxies,timeout=5)
                return {"id":response.json()["data"]["id"],"ip":ip}
            except:
                print("扫描失败，重试中...")
                retry_time+=1
        print("重试100次均失败，请检查网络！")
        return False



    def GetReport(self,data):
        scan_id=data["id"]
        ip=data["ip"]
        retry_time=0
        get_url = "https://www.virustotal.com/ui/analyses/" + scan_id
        while retry_time<5:
            agent=self.GetAgent()
            proxies = {"https": ip}
            print("正在获取报告：",get_url, "使用ip代理：", ip)#,"  使用UA：",agent)
            try:
                response = requests.get(get_url, headers={
                    #"User-Agent": agent,
                    "Referer": "https://www.virustotal.com/"},proxies=proxies,timeout=10)
                print("获取报告成功")
                #print(response.json())
                return {"malicious":response.json()["data"]["attributes"]["stats"]['malicious'],"suspicious":response.json()["data"]["attributes"]["stats"]['suspicious']}
            except:
                print("获取报告失败，重试中...")
                time.sleep(20)
                retry_time+=1
        print("重试5次获取报告均失败，请检查网络！")
        return False

    def GetAgent(self):
        return random.choice(self.agents)

    def GetIP(self):
        return random.choice(self.ip)

if __name__=="__main__":
    lablor=virustotal()
    url="179.43.147.227"
    res=lablor.label(url)
    print(res)
