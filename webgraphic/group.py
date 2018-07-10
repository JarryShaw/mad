import re
class group:
    def __init__(self,http,timestamp,IP,is_PC):
        #self.node_tree=[(uri,-1,0)]   #this is a normal tree of http nodes
        self.node_tree=[-1]
        self.http_info=[http]
        self.id=[timestamp]     #id(timestamp)is used to identify one unique http request
        self.alone=True
        self.IP=[]
        self.IP.append(list(IP))
        self.PC=is_PC
        self.ref_domain=""

        self.user_clicktion=False

    def add_merge(self,child,parent_id):    #
        '''
        total_level=len(self.level_location)-1
        index=self.http_info.index(parent)
        if (self.node_tree[index][-1] + 1) < len(self.level_location):
            level_index=self.level_location[self.node_tree[index][-1]+1]
        else:  # which means there is a new level of the tree
            start = len(self.node_tree)
            self.level_location.append(start)
            count=0
            for x in child.node_tree:
                if x[1]==-1:
                    self.node_tree.append((x[0],index,total_level+1))
                else:
                    self.node_tree.append((x[0],x[1]+start,total_level+1+x[2]))
                self.http_info.append(child.http_info[count])
                count+=1
                self.alone=False
                return True
        #otherwise insert the child and the children of the child to the tree
        '''
        index = self.id.index(parent_id)
        start=len(self.node_tree)
        count=0
        for x in child.node_tree:
            if x[1] == -1:
                self.node_tree.append(index)
            else:
                self.node_tree.append((x[0], x[1] + start))
            self.http_info.append(child.http_info[count])
            self.id.append(child.id[count])
            count += 1
            self.alone = False
            return True


    def exist(self,id):
        return id in self.id

    def set_user_click(self):
        self.user_clicktion=True

    def is_alone(self):
        if len(self.id) >1:
            self.alone=False
        return self.alone

    def is_PC(self):
        return self.PC

    def set_not_alone(self):
        self.alone=False

    def set_ref_domain(self,ref):
        self.ref_domain=ref

    #add according to referer
    def add(self,http,timestamp,parent_id,IP):
        self.alone=False
        index=self.id.index(parent_id)
        self.node_tree.append(index)
        self.http_info.append(http)
        self.id.append(timestamp)
        self.IP.append(list(IP))
        return True

    def get_children_num(self,id):
        count=0
        tmp=[]
        index=self.id.index(id)
        for x in range(len(self.node_tree)):
            if self.node_tree[x] ==index:
                count+=1
                tmp.append(x)
        while tmp:
            parent_size = len(tmp)
            for m in tmp:
                for n in range(len(self.node_tree)):
                    if self.node_tree[n]==m:
                        count+=1
                        tmp.append(n)
            for i in range(parent_size):
                tmp.pop(0)
        return count

    #delay time between child and its parent
    #return -1 if the node has no parent
    def get_delay(self,id):
        parent_index=self.node_tree[self.id.index(id)]
        if parent_index==-1:
            return -1
        delay=id-self.id[parent_index]
        return delay

    def getUrlById(self,id):
        index=self.id.index(id)
        http=self.http_info[index]
        ptr_Url1 = "Host.*?\\\\r"
        ptr_Url2 = "/.*?HTTP"
        tmp = re.findall(ptr_Url2, http)[0]
        tmp=tmp.strip(" HTTP")
        url=re.findall(ptr_Url1, http)[0].strip("\\r").strip("Host: ")+tmp
        return url

    def getDomain(self):
        ptr_Url1 = "Host.*?\\\\r"
        http = self.http_info[0]
        return re.findall(ptr_Url1, http)[0].strip("\\r").strip("Host: ")