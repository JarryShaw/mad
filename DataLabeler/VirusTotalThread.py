import threading

class ViruTotalThread(threading.Thread):
    def __init__(self,virustotal,queue,queue_result,counter):
        threading.Thread.__init__(self)
        self.scanner=virustotal
        self.que=queue
        self.que_result=queue_result
        self.counter=counter
        #print("线程启动")

    def run(self):
        while not self.que.empty():
            index=self.que.qsize()
            print("正在扫描第",index,"个url")
            url=self.que.get(timeout=5)
            result=self.scanner.label(url)
            if not result:
                print("网络有问题，线程关闭。")
                self.que.put(url,timeout=5)
                self.que_result.put({"url":url,"malicious":0,"suspicious":0,"state":0})
                return False
            self.que_result.put({"url":url,"malicious":result['malicious'],"suspicious":result['suspicious'],"state":1})
            self.counter = self.counter - 1
            print("第",index,"个url扫描完毕","还剩下",self.counter,"个url需要扫描")
        print("扫描完毕，线程关闭")
        return True
