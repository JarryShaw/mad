# -*- coding: utf-8 -*-


import collections
import datetime as dt
import ipaddress
import json
import os
import pathlib
import pprint ###
import shutil
import signal
import sys
import time

import numpy as np
import tensorflow as tf
from user_agents import parse as _parse

from make_stream import *
# from useragents.useragents import parse
from StreamManager.StreamManager4 import *


path = os.path.dirname(os.path.abspath(__file__))

DataPath = sys.argv[1]
ModelPath = sys.argv[2]
mode = sys.argv[3]
T = sys.argv[4]
ppid = int(sys.argv[5])

TrainRate = 0.8

tf.logging.set_verbosity(tf.logging.INFO)

# 输入为[批大小，宽度，高度，深度]
# -1代表自动处理当前大小
INPUTSHAPE = [-1, 32, 32, 1]  # 输入形状

# 第一层卷积层输入形状为[批大小，32，32，1]
# 第一层卷积层输出形状为[批大小，32，32，32]
FILTER1_NUM = 32  # 第一层滤波器数量
FILTER1_SHAPE = [5, 5]  # 第一层滤波器形状

# 第一层池化层输入形状为[批大小，32，32，32]
# 第一层池化层输出形状为[批大小，16，16，32]
POOL1_SHAPE = [2, 2]  # 第一层池化层形状
POOL1_STRIDE = 2  # 第一层池化层步长

# 第二层卷积层输入形状为[批大小，16，16，32]
# 第二层卷积层输出形状为[批大小，16，16，64]
FILTER2_NUM = 64  # 第二层滤波器数量
FILTER2_SHAPE = [5, 5]  # 第二层滤波器形状

# 第二层池化层输入形状为[批大小，16，16，64]
# 第二层池化层输出形状为[批大小，8，8，64]
POOL2_SHAPE = [2, 2]  # 第二层池化层形状
POOL2_STRIDE = 2  # 第二层池化层步长

# 展平前输入形状为[批大小，8，8，64]
# 展平后形状为[批大小，8*8*64]
FLAT_SHAPE = [-1, 8 * 8 * 64]  # 展平后形状

# 全连接层输入形状为[批大小，7*7*64]
# 全连接层输出个数为[批大小，1024]
DENSE_UNIT = 1024  # 全连接层输出个数

# 按概率丢弃神经元，避免过拟合
DROPOUT_RATE = 0.4  # 丢弃概率

# 输出个数，代表分类结果
OUTPUT_UNIT = 2

# 学习率
LEARNING_RATE = 0.001


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return {'val': obj.hex(), '_spec_type': 'bytes'}
        else:
            return super().default(obj)


def object_hook(obj):
    _spec_type = obj.get('_spec_type')
    if _spec_type:
        if _spec_type == 'bytes':
            return bytes.fromhex(obj['val'])
        raise ParseError(f'unknown {_spec_type}')
    return obj


def parse(ua):
    info = _parse(ua)

    _list = str(info).split(' / ')

    _type = list()
    if info.is_mobile:
        _type.append('Mobile')
    if info.is_tablet:
        _type.append('Tablet')
    if info.is_touch_capable:
        _type.append('Touch Capable')
    if info.is_pc:
        _type.append('PC')
    if info.is_bot:
        _type.append('Bot')

    _dict = dict(
        device=_list[0],
        os=_list[1],
        browser=_list[2],
        type=' / '.join(_type) or 'Other',
    )
    pprint.pprint(_dict) ###
    return _dict


def ReadDictionary(path, T):
    # file = open(path+"index.json")
    # files = json.load(file)[T]
    files = {
        '0' : [os.path.join(path, T, '0', file) for file in os.listdir(os.path.join(path, T, '0'))],
        '1' : [os.path.join(path, T, '1', file) for file in os.listdir(os.path.join(path, T, '1'))],
    }
    return files


def ReadEvaluateData(path, T):
    files = ReadDictionary(path, T)
    packets_0 = []
    for file in files['0']:
        packet = []
        payload = open(file, 'rb').read()
        if len(payload) < 1024:
            payload += (1024 - len(payload)) * b'\x00'
        elif len(payload) > 1024:
            payload = payload[:1024]
        for i in payload:
            packet.append(i)
        packets_0.append(packet)
    packets_1 = []
    for file in files['1']:
        packet = []
        payload = open(file, 'rb').read()
        if len(payload) < 1024:
            payload += (1024 - len(payload)) * b'\x00'
        elif len(payload) > 1024:
            payload = payload[:1024]
        for i in payload:
            packet.append(i)
        packets_1.append(packet)
    packets_0 = np.asarray(packets_0, np.float32)
    packets_1 = np.asarray(packets_1, np.float32)
    return packets_0, packets_1


def ReadTrainData1(path, T):
    files = ReadDictionary(path, T)
    packets_1 = []
    labels_1 = []
    packets_0 = []
    labels_0 = []
    for file in files['1']:
        packet = []
        payload = open(file, 'rb').read()
        if len(payload) < 1024:
            payload += (1024 - len(payload)) * b'\x00'
        elif len(payload) > 1024:
            payload = payload[:1024]
        for i in payload:
            packet.append(i)
        packets_1.append(packet)
        labels_1.append(1)
    for file in files['0']:
        packet = []
        payload = open(file, 'rb').read()
        if len(payload) < 1024:
            payload += (1024 - len(payload)) * b'\x00'
        elif len(payload) > 1024:
            payload = payload[:1024]
        for i in payload:
            packet.append(i)
        packets_0.append(packet)
        labels_0.append(0)

    packets_1 = np.asarray(packets_1, np.float32)
    labels_1 = np.asarray(labels_1, np.int32)
    shuffle = np.arange(len(packets_1))
    np.random.shuffle(shuffle)
    packets_1 = packets_1[shuffle]
    labels_1 = labels_1[shuffle]

    packets_0 = np.asarray(packets_0, np.float32)
    labels_0 = np.asarray(labels_0, np.int32)
    shuffle = np.arange(len(packets_0))
    np.random.shuffle(shuffle)
    packets_0 = packets_0[shuffle]
    labels_0 = labels_0[shuffle]

    packets_train = np.asarray(list(packets_1) + list(packets_0))
    labels_train = np.asarray(list(labels_1) + list(labels_0))

    packets_train = np.asarray(packets_train, np.float32)
    labels_train = np.asarray(labels_train, np.int32)
    shuffle = np.arange(len(packets_train))
    np.random.shuffle(shuffle)
    packets_train = packets_train[shuffle]
    labels_train = labels_train[shuffle]

    return packets_train, labels_train


def ReadTrainData2(index, T):
    files = index
    packets_1 = []
    labels_1 = []
    packets_0 = []
    labels_0 = []
    for file in files['1']:
        packet = []
        payload = open(file, 'rb').read()
        if len(payload) < 1024:
            payload += (1024 - len(payload)) * b'\x00'
        elif len(payload) > 1024:
            payload = payload[:1024]
        for i in payload:
            packet.append(i)
        packets_1.append(packet)
        labels_1.append(1)
    for file in files['0']:
        packet = []
        payload = open(file, 'rb').read()
        if len(payload) < 1024:
            payload += (1024 - len(payload)) * b'\x00'
        elif len(payload) > 1024:
            payload = payload[:1024]
        for i in payload:
            packet.append(i)
        packets_0.append(packet)
        labels_0.append(0)

    packets_1 = np.asarray(packets_1, np.float32)
    labels_1 = np.asarray(labels_1, np.int32)
    shuffle = np.arange(len(packets_1))
    np.random.shuffle(shuffle)
    packets_1 = packets_1[shuffle]
    labels_1 = labels_1[shuffle]

    packets_0 = np.asarray(packets_0, np.float32)
    labels_0 = np.asarray(labels_0, np.int32)
    shuffle = np.arange(len(packets_0))
    np.random.shuffle(shuffle)
    packets_0 = packets_0[shuffle]
    labels_0 = labels_0[shuffle]

    packets_train = np.asarray(list(packets_1) + list(packets_0))
    labels_train = np.asarray(list(labels_1) + list(labels_0))

    packets_train = np.asarray(packets_train, np.float32)
    labels_train = np.asarray(labels_train, np.int32)
    shuffle = np.arange(len(packets_train))
    np.random.shuffle(shuffle)
    packets_train = packets_train[shuffle]
    labels_train = labels_train[shuffle]

    return packets_train, labels_train


def ReadPredictData(index, T):
    files = index[T]
    packets = []
    names = []
    for file in files['0']:
        packet = []
        payload = open(file, 'rb').read()
        if len(payload) < 1024:
            payload += (1024 - len(payload)) * b'\x00'
        elif len(payload) > 1024:
            payload = payload[:1024]
        for i in payload:
            packet.append(i)
        packets.append(packet)
        names.append(file)
    packets = np.asarray(packets, np.float32)
    return packets, names


def NeutralNetwork(features, labels, mode):
    # 重置输入形状
    input_layer = tf.reshape(features["packet"], INPUTSHAPE)

    # 第一层卷积层，创建FILTER1_NUM个形状为FILTER1_SHAPE的滤波器
    # 采用默认步长(1, 1)，卷积结果填充为与输入相同大小
    # 使用激活函数max(feature, 0)
    conv1 = tf.layers.conv2d(
        inputs=input_layer,
        filters=FILTER1_NUM,
        kernel_size=FILTER1_SHAPE,
        padding="same",
        activation=tf.nn.relu)

    # 第一层池化层，采用形状为POOL1_SHAPE，步长为POOL1_STRIDE
    pool1 = tf.layers.max_pooling2d(
        inputs=conv1,
        pool_size=POOL1_SHAPE,
        strides=POOL1_STRIDE)

    # 第一层卷积层，创建FILTER2_NUM个形状为FILTER2_SHAPE的滤波器
    # 采用默认步长(1, 1)，卷积结果填充为与输入相同大小
    # 使用激活函数max(feature, 0)
    conv2 = tf.layers.conv2d(
        inputs=pool1,
        filters=FILTER2_NUM,
        kernel_size=FILTER2_SHAPE,
        padding="same",
        activation=tf.nn.relu)

    # 第一层池化层，采用形状为POOL2_SHAPE，步长为POOL2_STRIDE
    pool2 = tf.layers.max_pooling2d(
        inputs=conv2,
        pool_size=POOL2_SHAPE,
        strides=POOL2_STRIDE)

    # 展平输出为[批大小, FLAT_SHAPE]
    pool2_flat = tf.reshape(
        tensor=pool2,
        shape=FLAT_SHAPE)

    # 全连接层，输出为[批大小, DENSE_UNIT]
    # 使用激活函数max(feature, 0)
    dense = tf.layers.dense(
        inputs=pool2_flat,
        units=DENSE_UNIT,
        activation=tf.nn.relu)

    # 按DROPOUT_RATE随机丢弃神经元
    dropout = tf.layers.dropout(
        inputs=dense,
        rate=DROPOUT_RATE,
        training=mode == tf.estimator.ModeKeys.TRAIN)

    # 逻辑回归层，最终获得OUTPUT_UNIT个输出
    logits = tf.layers.dense(
        inputs=dropout,
        units=OUTPUT_UNIT)

    # 预测
    predictions = {
        # argmax返回第axis的索引所对应的最大值的索引
        # logits形状为[批大小, 2]，则其返回每一批中
        # 最大值的索引——0或1
        "classes": tf.argmax(input=logits, axis=1),
        # 默认对最后一个维度计算softmax函数
        "probabilities": tf.nn.softmax(logits, name="softmax_tensor")}

    # 如果目前是预测状态，返回预测结果
    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)

    # 目前不是预测状态，获得损失函数
    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)

    # 配置训练操作
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=LEARNING_RATE)
        train_op = optimizer.minimize(
            loss=loss,
            global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode=mode, loss=loss, train_op=train_op)

    # 添加评价指标
    eval_metric_ops = {
        "accuracy": tf.metrics.accuracy(
            labels=labels,
            predictions=predictions["classes"])}
    return tf.estimator.EstimatorSpec(
        mode=mode,
        loss=loss,
        eval_metric_ops=eval_metric_ops)


def main(unused):
    classifier = tf.estimator.Estimator(
        model_fn=NeutralNetwork,
        model_dir=ModelPath)

    # Before this system is placed, used for training initial model
    if mode == "train":
        packets_train, labels_train = ReadTrainData1(DataPath, T)
        tensors_to_log = {"probabilities": "softmax_tensor"}
        logging_hook = tf.train.LoggingTensorHook(
            tensors=tensors_to_log,
            every_n_iter=50)
        train_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"packet": packets_train},
            y=labels_train,
            batch_size=100,
            num_epochs=None,
            shuffle=True)
        classifier.train(
            input_fn=train_input_fn,
            steps=20000,
            hooks=[logging_hook])

    # When this system is placed, used for retaining model and fingerprinting.
    elif mode == "retrain":
        # files = [os.path.join(DataPath, x) for x in os.listdir(DataPath) if os.path.isfile(DataPath + x)]
        # index = dataset(*files, mode=1)
        index = ReadDictionary(DataPath, T)
        print(index)
        packets_train, labels_train = ReadTrainData2(index, T)
        tensors_to_log = {"probabilities": "softmax_tensor"}
        logging_hook = tf.train.LoggingTensorHook(
            tensors=tensors_to_log,
            every_n_iter=50)
        train_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"packet": packets_train},
            y=labels_train,
            batch_size=100,
            num_epochs=None,
            shuffle=True)
        classifier.train(
            input_fn=train_input_fn,
            steps=20,
            hooks=[logging_hook])

    # Used for system operating
    elif mode == "predict":
        start = time.time()
        print(start)
        # useragents = parse()
        # files = [os.path.join(DataPath, x) for x in os.listdir(DataPath) if os.path.isfile(DataPath + x)]
        # index = dataset(*files, mode=2)
        with open(os.path.join(DataPath, 'filter.json'), 'r') as file:
            data_index = json.load(file, object_hook=object_hook)
        data_index[T] = ReadDictionary(DataPath, T)
        # print('data_index:', data_index) ###
        isMalicious = data_index["is_malicious"]
        isClean = data_index["is_clean"]
        packets, names = ReadPredictData(data_index, T)
        print('names:', names) ###
        if names:
            predict_input_fn = tf.estimator.inputs.numpy_input_fn(
                x={"packet": packets},
                num_epochs=1,
                shuffle=False)
            predictions = list(classifier.predict(input_fn=predict_input_fn))
            predicted_classes = [p["classes"] for p in predictions]
        else:
            predicted_classes = list()
        with open(os.path.join(DataPath, "groups.json"), "r") as file:
            group = json.load(file, object_hook=object_hook)
        with open(os.path.join(DataPath, "record.json"), "r") as file:
            group_data = json.load(file, object_hook=object_hook)
        # group_data = dict()
        # for ipua in group[T]:
        #     for file in group[T][ipua]:
        #         name = pathlib.Path(file['filename']).stem
        #         group_data[name] = [file, ipua]
        # print("detected by fingerprint:")
        Malicious = []
        group_dict = {T: []}
        print('is_malicious:', isMalicious) ###
        for ipua in isMalicious:
            # print('ipua:', ipua, group[T].get(ipua, list())) ###
            for filedict in group[T].get(ipua, list()):
                filename = filedict["filename"]
                name = pathlib.Path(filename).stem
                # ipua = "UnknownUA"
                # temp = dict(UA="UnknownUA")
                # for key in group[T]:
                #     for file in group[T][key]:
                #         if name in file["filename"]:
                #             ipua = key
                #             temp = file
                #             break
                # src, dst, tstamp = name.split("-")
                # srcIP, srcPort = src.split("_")
                # dstIP, dstPort = dst.split("_")
                listname = name.split("_")
                temp_ip = ipaddress.ip_address(listname[0])
                if temp_ip.is_private:
                    srcIP = listname[0]
                    srcPort = listname[1]
                    dstIP = listname[2]
                    dstPort = listname[3]
                else:
                    srcIP = listname[2]
                    srcPort = listname[3]
                    dstIP = listname[0]
                    dstPort = listname[1]
                tstamp = listname[4]
                Malicious.append(dict(filedict,
                    is_malicious=1,
                    srcIP=srcIP,
                    srcPort=srcPort,
                    dstIP=dstIP,
                    dstPort=dstPort,
                    time=dt.datetime.fromtimestamp(float(tstamp)).isoformat(),
                    name=name,
                    ipua=filedict["ipua"],
                    info=parse(filedict["UA"]),
                    detected_by_cnn=False,
                ))
                group_dict[T].append(dict(
                    is_malicious=1,
                    type=filedict["type"],
                    filename=name + ".pcap",
                ))
        Clean = []
        print('is_clean:', isClean) ###
        for ipua in isClean:
            # print('ipua:', ipua, group[T].get(ipua, list())) ###
            for filedict in group[T].get(ipua, list()):
                filename = filedict["filename"]
                name = pathlib.Path(filename).stem
                # ipua = "UnknownUA"
                # temp = dict(UA="UnknownUA")
                # for key in group[T]:
                #     for file in group[T][key]:
                #         if name in file["filename"]:
                #             ipua = key
                #             temp = file
                #             break
                # src, dst, tstamp = name.split("-")
                # srcIP, srcPort = src.split("_")
                # dstIP, dstPort = dst.split("_")
                listname = name.split("_")
                temp_ip = ipaddress.ip_address(listname[0])
                if temp_ip.is_private:
                    srcIP = listname[0]
                    srcPort = listname[1]
                    dstIP = listname[2]
                    dstPort = listname[3]
                else:
                    srcIP = listname[2]
                    srcPort = listname[3]
                    dstIP = listname[0]
                    dstPort = listname[1]
                tstamp = listname[4]
                Clean.append(dict(filedict,
                    is_malicious=0,
                    srcIP=srcIP,
                    srcPort=srcPort,
                    dstIP=dstIP,
                    dstPort=dstPort,
                    time=dt.datetime.fromtimestamp(float(tstamp)).isoformat(),
                    name=name,
                    ipua=ipua,
                    info=parse(filedict["UA"]),
                    detected_by_cnn=False,
                ))
        val, url = StreamManager(NotImplemented, DataPath).validate(group_dict)
        for item in Malicious:
            flag = int(item["name"]+".pcap" in val)
            item["is_malicious"] = flag
            if flag:
                ind = val.index(item["name"]+".pcap")
                item["malicious_url"] = url[ind]
            else:
                item["malicious_url"] = None
        # print("detected by CNN: ")
        CNNClean = list()
        CNNMalicious = list()
        group_dict = {T: []}
        for i, kind in enumerate(predicted_classes):
            name = pathlib.Path(names[i]).stem
            listname = name.split("_")
            temp_data = group_data[name]
            temp_ip = ipaddress.ip_address(listname[0])
            if temp_ip.is_private:
                srcIP = listname[0]
                srcPort = listname[1]
                dstIP = listname[2]
                dstPort = listname[3]
            else:
                srcIP = listname[2]
                srcPort = listname[3]
                dstIP = listname[0]
                dstPort = listname[1]
            tstamp = listname[4]
            temp_dict = dict(temp_data,
                is_malicious=int(kind),
                srcIP=srcIP,
                srcPort=srcPort,
                dstIP=dstIP,
                dstPort=dstPort,
                time=dt.datetime.fromtimestamp(float(tstamp)).isoformat(),
                name=name,
                ipua=temp_data["ipua"],
                info=parse(temp_data["UA"]),
                detected_by_cnn=True,
            )
            if kind == 1:
                CNNMalicious.append(temp_dict)
                group_dict[T].append(dict(
                    is_malicious=1,
                    type=temp_data["type"],
                    filename=name + ".pcap",
                ))
            else:
                CNNClean.append(temp_dict)
                # paths = pathlib.Path(names[i])
                # group = paths.parts[-4]
                # name = paths.stem
                # groupPath = os.path.join(path, "stream/"+group)
                # stream = json.load(open(os.path.join(groupPath, "stream.json"), 'r'))[T]
                # for ua in stream:
                #     for file in stream[ua]:
                #         if name in file["filename"]:
                #             print(ua)
                # ipua = "UnknownUA"
                # temp = dict(UA="UnknownUA")
                # for key in group[T]:
                #     for file in group[T][key]:
                #         if name in file["filename"]:
                #             ipua = key
                #             temp = file
                #             break
                # src, dst, tstamp = name.split("-")
                # srcIP, srcPort = src.split("_")
                # dstIP, dstPort = dst.split("_")
                # listname = name.split("_")
                # srcIP = listname[0]
                # srcPort = listname[1]
                # dstIP = listname[2]
                # dstPort = listname[3]
                # tstamp = listname[4]
        # print("checking...")
        # group_dict = {T: []}
        # for i in Malicious:
        #     # paths = pathlib.Path(i)
        #     # paths = os.path.splitext(i)[0].split("/")
        #     # group = paths.parts[-4]
        #     # name = paths.stem
        #     # if group not in group_dict:
        #     #     group_dict[group] = {}
        #     #     group_dict[group]["Background_PC"] = []
        #     # tmp_dict = {}
        #     # tmp_dict["is_malicious"] = 1
        #     # tmp_dict["type"] = 0
        #     # tmp_dict["filename"] = i["name"] + ".pcap"
        #     group_dict[T].append(dict(i,
        #         is_malicious=1,
        #         type=0,
        #         filename=i["name"] + ".pcap",
        #     ))
        # val = []
        # for i in group_dict:
        #     streamPath = os.path.join(path, "stream/"+i)
        #     datasetPath = os.path.join(path, "dataset/"+i)
        #     retrainPath = os.path.join(path, "retrain/Backgroud_PC/0")
        #     if not os.path.exists(retrainPath):
        #         os.mkdir(retrainPath)
        #     val += StreamManager.validate(group_dict[i], root=streamPath)
        #     for j in val:
        #         shutil.copy(os.path.join(datasetPath, "Background_PC/0/"+j[:-4]+"dat"), retrainPath)
        stem = pathlib.Path(DataPath).name
        val, url = StreamManager(NotImplemented, DataPath).validate(group_dict)
        loss = 1 - (len(val)/sum(predicted_classes) if sum(predicted_classes) else 1.0)
        # print('### Testing:', len(val), val, sum(predicted_classes), predicted_classes) ###
        loss_record = list()
        if os.path.isfile("/usr/local/mad/loss.json"):
            with open("/usr/local/mad/loss.json", "r") as file:
                loss_record = json.load(file, object_hook=object_hook)
        print("loss:", loss)
        loss_record.append(dict(
            time=stem,
            loss=loss,
        ))
        with open("/usr/local/mad/loss.json", "w") as file:
            json.dump(loss_record, file, cls=JSONEncoder)
        if loss > 0.5:
            print(f'{DataPath} needs retrain...')
            try:
                os.kill(ppid, signal.SIGUSR2)
            except ProcessLookupError:
                print(f"ProcessLookupError: Process {ppid} not found")
        end = time.time()
        print(end)
        print('Running time: %s Seconds' % (end - start))
        retrain_index = load_stream()
        # if os.path.isfile("/usr/local/mad/retrain/stream.json"):
        #     while True:
        #         try:
        #             with open("/usr/local/mad/retrain/stream.json", 'r') as file:
        #                 retrain_index.update(json.load(file, object_hook=object_hook))
        #         except json.decoder.JSONDecodeError:
        #             continue
        #         break
        for kind in {'Background_PC',}:
            retrain_index[kind] = collections.defaultdict(list, retrain_index[kind])
        for item in CNNMalicious:
            flag = int(item["name"]+".pcap" in val)
            item["is_malicious"] = flag
            if flag:
                ind = val.index(item["name"]+".pcap")
                item["malicious_url"] = url[ind]
            else:
                item["malicious_url"] = None
            name = stem+"_"+item["name"]
            retrain_index[T][item["ipua"]].append(item)
            shutil.copy(os.path.join(DataPath, T, "0", item["name"]+".dat"),
                        os.path.join("/usr/local/mad/retrain", T, str(flag), name+".dat"))
            # print('src:', os.path.join(DataPath, T, "0", item["name"]+".dat"))
            # print('dst:', os.path.join("/usr/local/mad/retrain/dataset", T, str(flag), name+".dat"))
            # print('src:', os.path.join(DataPath, "stream", item["name"]+".pcap"))
            # print('dst:', os.path.join("/usr/local/mad/retrain/stream", T, str(flag), name+".pcap"))
            # shutil.copy(os.path.join(DataPath, "stream", item["name"]+".pcap"),
            #             os.path.join("/usr/local/mad/retrain/stream", T, str(flag), name+".pcap"))
        with open(os.path.join(DataPath, "stream.json"), 'w') as file:
            json.dump(retrain_index, file, cls=JSONEncoder)
        shutil.copy(os.path.join(DataPath, "stream.json"), '/usr/local/mad/retrain/stream.json')
        report = list()
        report.extend(Clean)
        report.extend(Malicious)
        report.extend(CNNClean)
        report.extend(CNNMalicious)
        pprint.pprint(report) ###
        with open(f"/usr/local/mad/report/{T}/{stem}.json", 'w') as file:
            json.dump(report, file, cls=JSONEncoder)
        report_index = list(map(lambda name: f"/report/{T}/{name}",
                        filter(lambda name: name != "index.json",
                            sorted(os.listdir(f"/usr/local/mad/report/{T}")))))
        with open(f"/usr/local/mad/report/{T}/index.json", 'w') as file:
            json.dump(report_index, file, cls=JSONEncoder)
            # files = [f"/report/{T}/{name}"
            #             for name in os.listdir(f"/usr/local/mad/report/{T}")
            #             if name != "index.json"]

    # Used for evaluating our system
    elif mode == "evaluate":
        packets_predict_0, packets_predict_1 = ReadEvaluateData(DataPath, T)
        predict_input_fn_0 = tf.estimator.inputs.numpy_input_fn(
            x={"packet": packets_predict_0},
            num_epochs=1,
            shuffle=False)
        predictions_0 = list(classifier.predict(input_fn=predict_input_fn_0))
        predicted_classes_0 = [p["classes"] for p in predictions_0]
        predict_input_fn_1 = tf.estimator.inputs.numpy_input_fn(
            x={"packet": packets_predict_1},
            num_epochs=1,
            shuffle=False)
        predictions_1 = list(classifier.predict(input_fn=predict_input_fn_1))
        predicted_classes_1 = [p["classes"] for p in predictions_1]
        print("result:")
        print("negative samples: %d" % len(predicted_classes_0))
        print("prediction negative samples: %d" % sum(predicted_classes_0))
        print("true negative rate: %f" % (1-sum(predicted_classes_0)/len(predicted_classes_0)))
        print("positive samples: %d" % len(predicted_classes_1))
        print("prediction positive samples: %d" % sum(predicted_classes_1))
        print("true positive rate: %f" % (sum(predicted_classes_1)/len(predicted_classes_1)))


if __name__ == '__main__':
    tf.app.run()
