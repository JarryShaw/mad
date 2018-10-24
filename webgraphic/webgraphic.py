#from scapy.all import *
import dpkt
from webgraphic.group import *
import math
import time
import os
import socket

class webgraphic:
    def __init__(self):
        self.tmp_mem=[]
        self.tmp_index=[]
        self.path=os.path.dirname(os.path.abspath(__file__))#os.getcwd()
        self.groups = []
        self.twd_size=10.0    #the size of the time window
        self.filetered_ip=[]
        self.source = 0
        self.ptr = ".*(GET|POST|HEAD).*HTTP.*" #判断是否为GET/POST/HEAD包
        self.exptr = "Host.*?\\\\r" #匹配取出domain
        self.reptr = "Referer.*?\\\\r"  #匹配取出referer
        self.urptr = "/.*?\\?"    #匹配取出uri(不带参数)
        self.urptr2 = "/.*?HTTP"   #匹配取出uri(带了参数)

        self.UserAgent="User-Agent.*?\\\\r"
        keywords=['nokia','sony',"meipai",'ericsson','mot','samsung','htc','sgh','lg','sharp','sie-',
                'philips','panasonic','alcatel','lenovo','iphone','ipod', 'blackberry','meizu',
                'android','netfront','symbian','ucweb','windowsce','palm',
                'operamini','operamobi','openwave','nexusone','cldc','midp','wap','mobile','phone'
                  'Phone','CFNetwork','Mobile']
        tmp=""
        for x in keywords:
            tmp+=(x+"|")
        self.FromPhone=".*("+tmp+"Android).*"
        #print(self.FromPhone)

        keywords2=["\\.html","\\.css","\\.aspx","\\.asp","\\.js"]
        tmp=""
        for i in range(len(keywords2)):
            if i!=(len(keywords2)-1):
                tmp+=(keywords2[i]+"|")
            else:
                tmp+=keywords2[i]
        self.HeadContent=".*("+tmp+").*"
        print(self.HeadContent)

        #read in the top 10K safe domain
        self.filter=[]
        self.filter_recently=[]
        self.recent_three=[]
        self.recent_index = 0
        #file=open(self.path+"/webgraphic/top-10k.txt",'r')
        file=open(self.path+"/top-10k.txt",'r')
        line=file.readline()
        while line:
            self.filter.append(line.strip("\n"))
            line=file.readline()



    def set_window_size(self,size):
        self.twd_size=float(size)

    def hit_filter(self,domain):
        flag=False
        '''
        for x in self.recent_three:
            if x in domain:
                return True
      '''
        for x in self.filter_recently:
            if x in domain:
                #if x not in self.recent_three:
                #    if len(self.recent_three)==3:
                #        self.recent_three[self.recent_index%3]=x
                #        self.recent_index+=1
                #   else:
                #        self.recent_three.append(x)
                return True
        for x in self.filter:
            if x in domain:
                if x not in self.filter_recently:
                    self.filter_recently.append(x)
                #if x not in self.recent_three:
                #    if len(self.recent_three)==3:
                #        self.recent_three[self.recent_index%3]=x
                #        self.recent_index+=1
                #    else:
                #        self.recent_three.append(x)
                flag=True
                break
        return flag

    def read_in(self,filename):
        f = open(filename, "rb")
        self.source = dpkt.pcap.Reader(f)
        start=time.time()
        no_referer=0
        #self.source = PcapReader(filename)
        packet = dpkt_next(self.source)
        total_num = 0
        filtered_num=0
        empty=0
        empty_pack=[]
        count_PC=0
        count_phone=0
        sttt=packet[0]
        e=0
        while packet:
            e = packet[0]
            p = dpkt.ethernet.Ethernet(packet[1])
            s = packet_to_str(packet)
            '''
            try:
                s = str(packet[Raw].load)
            except:
                packet = self.source.read_packet()
                continue
           '''
            if re.match(self.ptr, s):
                #print(s)
                timestamp=packet[0]
                #print("time:  ",timestamp)
                #ip=[packet[IP].src,packet[IP].dst]
                ip=[socket.inet_ntoa(p.data.src),socket.inet_ntoa(p.data.dst)]
                ip.sort()

                #get uri and host domain
                try:
                    tmp_u = re.findall(self.urptr2, s)[0]
                except:
                    packet=dpkt_next(self.source)
                    continue
                if not re.findall(self.urptr, tmp_u):
                    tmp_u = tmp_u.strip(" HTTP")
                else:
                    tmp_u = re.findall(self.urptr, tmp_u)[0].strip("?")
                try:
                    uri = re.sub("Host: ","",re.findall(self.exptr, s)[0].strip("\\r")) + tmp_u
                    host = re.sub("Host: ","",re.findall(self.exptr, s)[0].strip("\\r"))
                    host=re.sub("/.*","",host)
                    # print(uri)
                except:
                    packet = dpkt_next(self.source)
                    print("无效包，跳过")
                    continue


                if(self.hit_filter(host)):
                    print("安全域名：",host,",filtered")
                    filtered_num+=1
                    if ip not in self.filetered_ip:
                        self.filetered_ip.append(ip)
                    packet = dpkt_next(self.source)
                    continue



                total_num+=1   #count valid http requests


                #remove outdated http request
                self.tmp_mem.append(packet)
                for k in range(len(self.tmp_mem)):
                    if (self.tmp_mem[k][0]+self.twd_size) < timestamp:
                        continue
                    else:
                        self.tmp_mem=self.tmp_mem[k:]
                        self.tmp_index=self.tmp_index[k:]
                        break

                is_PC=0
                # whether it is PC or phone
                try:
                    ua = re.findall(self.UserAgent,s)[0].strip("\\r")
                    ua=re.sub("User-Agent: ","",ua)
                    print(ua)
                except:
                    print("不存在UA")
                    empty+=1
                    empty_pack.append(s)
                    is_PC=2

                if is_PC!=2:
                    if re.match(self.FromPhone,ua):
                        is_PC=0
                        print("来自手机")
                        count_phone+=1
                    else:
                        is_PC=1
                        print("来自电脑")
                        count_PC+=1


                #find the referer of the new packet
                try:
                    ref=re.findall(self.reptr,s)[0].strip("\\r").strip("Referer: ").strip("http://")
                    ref=ref.strip("s://")
                    #print("-----------------------------------------------------")
                    #print(timestamp)
                    #print(ref)
                    #print("------"+s)
                except:
                    ref=0

                #if no referer,then set the new request as a new group\
                if not ref:
                    #print("unmatch!!!!   "+uri)
                    #print("host id   "+ host)
                    #print("包的内容为："+s)
                    no_referer+=1


                    flag=False
                    #print("尝试规则4")
                    for k in range(len(self.tmp_mem)-1):
                        if(len(self.tmp_mem) - 2 - k)<0:
                            break
                        packet_tmp = self.tmp_mem[len(self.tmp_mem) - 2 - k]
                        s_tmp = packet_to_str(packet_tmp)
                        try:
                            domain_tmp = re.findall(self.exptr, s_tmp)[0].strip("\\r").strip("Host: ")
                        except:
                            continue
                        index = len(self.tmp_mem) - 2 - k
                        if self.IsSimilar(domain_tmp,host) and not self.groups[self.tmp_index[index]].is_alone() and self.groups[self.tmp_index[index]].is_PC()==is_PC:
                            #print("使用规则4连接")
                            #print(domain_tmp)
                            #print(host)
                            self.groups[self.tmp_index[index]].add(s, timestamp, packet_tmp[0],ip)
                            self.tmp_index.append(self.tmp_index[index])
                            flag = True
                            break
                    '''
                    for k in range(len(self.groups)):
                        group_tmp=self.groups[len(self.groups)-1-k]
                        if not group_tmp.is_alone() and group_tmp.getDomain()==host:
                            print("使用规则3连接")
                            self.groups[len(self.groups) - 1 - k].add(s,timestamp,group_tmp.id[0])
                            self.tmp_index.append(len(self.groups) - 1-k)
                            flag=True
                            break
                            '''
                    # print("尝试规则3")
                    if (re.match(self.HeadContent, uri) or is_PC==2)and not flag:
                        # print("内容决定为头结点")
                        self.groups.append(group(s, timestamp, ip, is_PC))
                        self.groups[-1].set_not_alone()
                        self.tmp_index.append(len(self.groups) - 1)
                        packet = dpkt_next(self.source)
                        continue
                    if not flag:
                        self.groups.append(group(s,timestamp,ip,is_PC))
                        self.tmp_index.append(len(self.groups)-1)
                    packet = dpkt_next(self.source)
                    continue
                #if there is a referer,then add the new request to that group
                else:
                    fflag=False
                    #print("---------------------------------")
                    #print(len(self.tmp_mem))
                    for k in range(len(self.tmp_mem)-1):
                        packet_tmp=self.tmp_mem[len(self.tmp_mem)-2-k]
                        s_tmp=packet_to_str(packet_tmp)
                        ttt = re.findall(self.urptr2, s_tmp)[0]
                        if not re.findall(self.urptr, ttt):
                            ttt = ttt.strip(" HTTP")
                        else:
                            ttt = re.findall(self.urptr, ttt)[0].strip("?")
                        try:
                            uri_tmp= re.findall(self.exptr, s_tmp)[0].strip("\\r").strip("Host: ") + ttt
                        except:
                            continue
                        uri_tmp=uri_tmp.strip("http://")
                        #print("searching.....",uri_tmp)
                        if uri_tmp==ref:
                            #print("hit88888888")
                            fflag=True
                            index=len(self.tmp_mem)-2-k
                            parent_id=packet_tmp[0]
                            try:
                                self.groups[self.tmp_index[index]].add(s,timestamp,parent_id,ip)
                            except:
                                #print(index)
                                #print(len(self.tmp_index))
                                exit(-1)
                            self.tmp_index.append(self.tmp_index[index])
                            break

                    #print("-----------------------------------------------------")
                    ffflag=False
                    if not fflag:
                        #print("尝试规则2：")
                        ref_domain_rule = ".*?/"
                        try:
                            ref_domain = re.findall(ref_domain_rule, ref)[0].strip("/")
                        except:
                            ref_domain = ref
                        #print("ref_domain为："+ref_domain)
                        for k in range(len(self.tmp_mem)-1):
                            packet_tmp = self.tmp_mem[len(self.tmp_mem) - 2 - k]
                            s_tmp = packet_to_str(packet_tmp)
                            try:
                                domain_tmp = re.findall(self.exptr, s_tmp)[0].strip("\\r").strip("Host: ")
                            except:
                                continue
                            index=len(self.tmp_mem) - 2 - k
                            if (self.IsSimilar(domain_tmp,ref_domain) or self.IsSimilar(self.groups[self.tmp_index[index]].ref_domain,ref_domain))and not self.groups[self.tmp_index[index]].is_alone() and self.groups[self.tmp_index[index]].is_PC()==is_PC:
                                #print("使用规则2连接")
                                #print(index)
                                #print(s_tmp)
                                #print(s)
                                #print("tmp_mem长度",len(self.tmp_mem))
                                #print("tmp_index长度",len(self.tmp_index))
                                self.groups[self.tmp_index[index]].add(s, timestamp, packet_tmp[0],ip)
                                self.tmp_index.append(self.tmp_index[index])
                                ffflag = True
                                break
                                '''
                        for k in range(len(self.groups)):
                            group_tmp = self.groups[len(self.groups) - 1 - k]
                            if not group_tmp.is_alone() and group_tmp.getDomain() == ref_domain:
                                print("使用规则2连接")
                                self.groups[len(self.groups) - 1 - k].add(s, timestamp, group_tmp.id[0])
                                self.tmp_index.append(len(self.groups) - 1 - k)
                                ffflag = True
                                break
                                '''
                        if not ffflag:
                            #print("孤独，成立新组！")
                            self.groups.append(group(s,timestamp,ip,is_PC))
                            self.groups[-1].set_not_alone()
                            self.groups[-1].set_ref_domain(ref_domain)
                            self.tmp_index.append(len(self.groups) - 1)

            packet = dpkt_next(self.source)
        '''
        for x in self.groups:
            if not x.is_alone():
                for m in x.IP:
                    print(m)
    '''
        end=time.time()
        t=end-start
        print("共读入",total_num,"个包")
        print("过滤掉的安全域名的包有:",filtered_num,"个")
        print("ua为空的有",empty,"个")
        print(float(empty)/total_num)
        print("没referer的包共有"+str(no_referer)+"个")
        print("tmp_mem:",len(self.tmp_mem))
        print("tmp_index:", len(self.tmp_index))
        print("来自手机的包共有",count_phone,"个")
        print("来自PC端的包",count_PC,"个")
        print("共有"+str(len(self.groups))+"个簇")
        #print("ua为空的包为")
        #for x in empty_pack:
        #    print(x)
        print("共耗时：",t,"s")
        print("数据时段:",e-sttt,"s")
        num_pc_bro=0
        for x in self.groups:
            if not x.is_alone() and x.is_PC()==1:
                num_pc_bro+=len(x.IP)
        num_pc_back=0
        for x in self.groups:
            if x.is_alone() and x.is_PC()==1:
                num_pc_back+=1
        num_phone_bro=0
        for x in self.groups:
            if not x.is_alone() and x.is_PC()==0:
                num_phone_bro+=len(x.IP)
        num_phone_back=0
        for x in self.groups:
            if x.is_alone() and x.is_PC()==0:
                num_phone_back+=1
        num_suspicious=0
        for x in self.groups:
            if x.is_PC()==2:
                num_suspicious+=len(x.id)
        print("PC浏览器数量: ",num_pc_bro)
        print("PC软件数量: ",num_pc_back)
        print("Phone浏览器数量: ",num_phone_bro)
        print("Phone软件数量: ",num_phone_back)
        print("无ua的嫌疑软件数量为:",num_suspicious)
        f.close()


    #get filtered ip list
    def get_filtered_ip(self):
        return self.filetered_ip


    #get all head http requests
    def get_head_packets(self):
        packets=[]     #in the form of (id,http_info)
        for x in self.groups:
            packets.append((x.id[0],x.http[0]))
        return packets

    #get all feature for identifying user cliction
    def get_all_features_fortrainer(self,labled_url):
        # features=["content type","response lenth","number of referrals","time gap","url lenth","advertisement","presence of parents",lable]
        features=[]
        ptr_Content="Content-Type.*?/"
        ptr_ResLenth="Content-Length.*?\\\\r"
        for x in self.groups:
            for i in range(len(x.id)):
                tmp=[]
                url=x.getUrlById(x.id[i])
                http=x.http_info[i]
                if re.findall(ptr_Content,http):
                    content_type=re.findall(ptr_Content,http)[0].strip("Content-Type: ").strip("/")
                else:
                    content_type="None"
                if re.findall(ptr_ResLenth,http):
                    #print(re.findall(ptr_ResLenth,http)[0].strip("Content-Length: ").strip("\\r"))
                    #print(http)
                    response_lenth=int(re.findall(ptr_ResLenth,http)[0].strip("Content-Length: ").strip("\\r"))
                else:
                    response_lenth=0
                number_of_ref=x.get_children_num(x.id[i])
                time_gap=x.get_delay(x.id[i])
                url_lenth=len(url)
                advertisement=0
                presence_of_parents =1
                if time_gap==-1:
                    presence_of_parents=0
                lable=0
                if url in labled_url:
                    lable=1
                tmp=[content_type,response_lenth,number_of_ref,time_gap,url_lenth,advertisement,presence_of_parents,lable]
                features.append(tmp)
        return features

    #
    def GetBrowserIP_PC(self):
        result=[]
        for x in self.groups:
            if not x.is_alone() and x.is_PC()==1:
                for m in x.IP:
                    if m not in result:
                        result.append(m)
        return result

    def GetIPS(self):
        ips=[]
        ips.append(self.GetBrowserIP_PC())
        ips.append(self.GetBackgroundIP_PC())
        ips.append(self.GetBrowserIP_Phone())
        ips.append(self.GetBackgroundIP_Phone())
        ips.append(self.GetSuspicious())
        ips.append(self.filetered_ip)
        return ips

    def GetSuspicious(self):
        result=[]
        for x in self.groups:
            if x.is_PC()==2:
                for m in x.IP:
                    if m not in result:
                        result.append(m)
        return result

    def GetBackgroundIP_PC(self):
        result = []
        for x in self.groups:
            if x.is_alone() and x.is_PC()==1:
                result.append(x.IP[0])
        return result

    def GetBrowserIP_Phone(self):
        result = []
        for x in self.groups:
            if not x.is_alone() and x.is_PC()==0:
                for m in x.IP:
                    if m not in result:
                        result.append(m)
        return result

    def GetBackgroundIP_Phone(self):
        result = []
        for x in self.groups:
            if x.is_alone() and x.is_PC()==0:
                result.append(x.IP[0])
        return result

    #set one head node related to another http_request
    def set_related(self,child_id,parent_id):
        index=self.getIndexById(child_id)
        if index==-1:
            print("not found,invalid children id!")
            return
        child_group=self.groups[index]
        parent_group=self.groups[self.getIndexByChildId(parent_id)]
        parent_group.add_merge(child_group,parent_id)

    #set a head node to be group cliction
    def set_UserCliction(self,id):
        index=self.getIndexById(id)
        self.groups[index].set_user_click()

        # get ids of http_requests with a given time window size

    #private method
    # get ids of http_requests with a given time window size
    def get_packet_twd(self, id, twd_size=2):
        index = self.getIndexById(id)
        if index == -1:
            print("invalid id!")
            return
        ids = []
        half_size = float(twd_size) / 2
        i = index - 1
        time = self.groups[index].id[0]
        while i > 0:
            if math.fabs(self.groups[i].id[0] - time) < half_size:
                for id in self.groups[i].id:
                    if math.fabs(id - time) < half_size:
                        ids.append(id)
            else:
                break
        i = index + 1
        while i < len(self.groups):
            if math.fabs(self.groups[i].id[0] - time) < half_size:
                for id in self.groups[i].id:
                    if math.fabs(id - time) < half_size:
                        ids.append(id)
            else:
                break
        return ids

    #private method
    def get_group_size(self,id):
        index=self.getIndexById(id)
        if index==-1:
            print("invalid id!")
            return -1
        return len(self.groups[index].id)

    #private method
    #get the num of children node of a http request,identified by its id
    def get_children_size(self,id):
        index=self.getIndexByChildId(id)
        if index==-1:
            print("invalid id!")
            return -1
        return self.groups[index].get_children_num(id)

    #private method
    #get the delay between a node and its parent,return -1 if it has no parent
    def get_delay(self,id):
        index = self.getIndexByChildId(id)
        if index==-1:
            print("invalid id!")
            return -1
        return self.groups[index].get_delay(id)

    #private method
    #get the group index of a head node
    def getIndexById(self,id):
        index = -1
        # 二分查找
        lenth = len(self.groups)
        low = 0
        high = lenth - 1
        middle = (low + high) / 2
        while middle != high:
            if self.groups[middle].id[0] < id:
                low = middle + 1
            elif self.groups[middle].id[0] > id:
                high = middle - 1
            else:
                index = middle
                break
        return index

    #private method
    #get the group index of a child node
    def getIndexByChildId(self,id):
        low=0
        high=len(self.groups)-1
        small=self.groups[low].id[0]
        big=self.groups[high].id[0]
        if id<small:
            return -1
        elif id >big:
            end=high
        else:
            while low!=high-1:
                middle = int((low + high) / 2)
                right = self.groups[middle].id[0]
                if right<=id:
                    small=right
                    low=middle
                else:
                    big=right
                    high=middle
        end=low
        for i in range(end):
            if self.groups[i].exist(id):
                return i
        return -1

    def NumNotAlone(self):
        count=0
        info=[]
        for x in self.groups:
            if not x.is_alone():
                count+=1
                info.append((x.http_info[0],len(x.id)))
        return info

    #private method
    #get the similarity between two domain
    def IsSimilar(self,domain1,domain2):
        #simple version 1

        stop_words=["www","com","cn","bbs","edu","gov","int","mil","net","org","biz","info","pro","name","museum","coop","aero"]
        words1=domain1.split(".")
        words2=domain2.split(".")
        for m in words1:
            if m in stop_words:
                words1.remove(m)
        for m in words2:
            if m in stop_words:
                words2.remove(m)
        if len(words2)==0 or len(words1)==0:
            return False
        if words1[-1]==words2[-1]:
                return True
        return False
        '''
        if domain1==domain2:
            return True
        else:
            return False
        '''

    def formatip(self,ip):
        tmp=ip.split('.')
        result=""
        for i in range(4):
            raw=""
            for x in range(3-len(tmp[i])):
                raw+="0"
            raw+=tmp[i]
            if i!=3:
                raw+='.'
            result+=raw
        return result



def dpkt_next(reader):
    try:
        p=next(reader)
        return p
    except:
        return None

def packet_to_str(packet):
    try:
        p = dpkt.ethernet.Ethernet(packet[1])
        s = str(p.data.data.pack()[p.data.data.__hdr_len__:])
    except:
        return "notvalid"
    return s
