from webgraphic.webgraphic import *
from StreamManager.StreamManager4 import *
builder=webgraphic()
builder.read_in("./stream/user/user.pcap")
IPS=builder.GetIPS()
print(IPS)
stream=StreamManager("user.pcap")
stream.generate()
stream.classify(IPS)
stream.Group()
stream.labelGroups()
typeone=stream.GetBrowserGroup_PC()
typetwo=stream.GetBackgroudGroup_PC()
typethree=stream.GetBrowserGroup_Phone()
typefour=stream.GetBackgroudGroup_Phone()
typefive=stream.GetSuspicious()

print("种类1恶意---------------------------------------")
for key in typeone:
    for x in typeone[key]:
        if x["is_malicious"]!=0 :
            print(key,typeone[key])
            break;

print("种类2恶意---------------------------------------")
for key in typetwo:
    for x in typetwo[key]:
        if x["is_malicious"]!=0 :
            print(key,typetwo[key])
            break;
print("种类3恶意---------------------------------------")
for key in typethree:
    for x in typethree[key]:
        if x["is_malicious"]!=0 :
            print(key,typethree[key])
            break;
print("种类4恶意---------------------------------------")
for key in typefour:
    for x in typefour[key]:
        if x["is_malicious"]!=0 :
            print(key,typefour[key])
            break;
print("种类5恶意---------------------------------------")
for key in typefive:
    for x in typefive[key]:
        if x["is_malicious"]!=0 :
            print(key,typefive[key])
            break;
