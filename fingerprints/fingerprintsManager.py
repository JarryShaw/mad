from fingerprints.fingerprint import *
from fingerprints.detection import *
import pickle
import os

class fingerprintManager:
    def __init__(self):
        # self.filepath="/home/ubuntu/MaliciousApplicationDetector/fingerprints/fingerprints"
        # self.filepath=os.path.dirname(os.path.abspath(__file__))+"fingerprints"
        self.filepath="/usr/local/mad/fingerprint.pickle"
        self.fingerprints={}
        self.detector=DetectionModule()
        if os.path.exists(self.filepath):
            with open(self.filepath,"rb") as f:
                self.fingerprints=pickle.load(f)
            f.close()

    def GenerateAndUpdate(self,stream_path,groups):
        Gen=FingerprintGenerator(stream_path)
        fingerprints=Gen.genrate(groups)
        for m in fingerprints:
            print(m,":")
            print(fingerprints[m])
        self.add_update(fingerprints)
        with open(self.filepath,"wb") as f:
            pickle.dump(self.fingerprints,f)
        f.close()


    def Identify(self,stream_path,groups):
        Gen=FingerprintGenerator(stream_path)
        fingerprints=Gen.genrate(groups)
        print("有",len(fingerprints),"个指纹")
        result={"is_malicious":[],"new_app":[],"is_clean":[]}
        for app in fingerprints:
            flag=False
            for old_app in self.fingerprints:
                if self.detector.similarity_check(fingerprints[app],self.fingerprints[old_app]):
                    print("new----------------------------------")
                    print(fingerprints[app])
                    print("old----------------------------------")
                    print(self.fingerprints[old_app])
                    flag=True
                    if self.fingerprints[old_app].is_malicious:
                        result["is_malicious"].append(app)
                    else:
                        result["is_clean"].append(app)
                    break
            if not flag:
                result["new_app"].append(app)
        print("识别出了",len(fingerprints)-len(result["new_app"]),"个指纹")
        return result


    def add_update(self,newfingerprints):
        print("Updating fingerprints ......")
        for app in newfingerprints:
            flag=False
            for old_app in self.fingerprints:
                if self.detector.similarity_check(newfingerprints[app],self.fingerprints[old_app]):
                    flag=True
                    break
            if not flag:
                self.fingerprints[app]=newfingerprints[app]
