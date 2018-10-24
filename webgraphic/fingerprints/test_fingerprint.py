from fingerprint import *
from detection import *

f=open("../stream/test3/test3.txt","r")
line=f.readline()
line=f.readline()
line=line.strip("\n")
dict_group=eval(line)

v=open("../stream/test4/test4.txt","r")
vline=v.readline()
vline=v.readline()
vline=vline.strip("\n")
validate=eval(vline)

detector=DetectionModule()

path="../stream/test3/tmp"
Gen=FingerprintGenerator(path)
fingerprints=Gen.genrate(dict_group)



path2="../stream/test4/tmp"
Gen2=FingerprintGenerator(path2)
fingerprints_validate=Gen2.genrate(validate)
total=len(fingerprints_validate)
identified=0

for app in fingerprints_validate:
    for key in fingerprints:
        if detector.similarity_check(fingerprints[key],fingerprints_validate[app]):
            print("指纹命中-------------------------------------------")
            identified+=1
            print(fingerprints[key])
            print(fingerprints_validate[app])
            print("---------------------------------------------------")
            break
print("总共有：",total,"个指纹")
print("识别出了：",identified,"个已知应用")
