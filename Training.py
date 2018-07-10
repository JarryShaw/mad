# -*- coding: utf-8 -*-

import json
import os
import pathlib
import sys
import shutil
import time

import numpy as np
import tensorflow as tf

from dataset import *
from StreamManager.StreamManager4 import *


path = os.path.dirname(os.path.abspath(__file__))


DataPath = sys.argv[1]
ModelPath = sys.argv[2]
mode = sys.argv[3]
T = sys.argv[4]

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


def ReadDictionary(path, T):
    file = open(path+"index.json")
    files = json.load(file)[T]
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
    files = index[T]
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
        files = [os.path.join(DataPath, x) for x in os.listdir(DataPath) if os.path.isfile(DataPath + x)]
        index = dataset(*files, mode=1)
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
        files = [os.path.join(DataPath, x) for x in os.listdir(DataPath) if os.path.isfile(DataPath + x)]
        index = dataset(*files, mode=2)
        print(index)
        isMalicious = index["is_malicious"]
        packets, names = ReadPredictData(index, T)
        predict_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"packet": packets},
            num_epochs=1,
            shuffle=False)
        predictions = list(classifier.predict(input_fn=predict_input_fn))
        predicted_classes = [p["classes"] for p in predictions]
        print("detected by fingerprint:")
        for i in isMalicious:
            print(i)
        print("detected by CNN: ")
        Malicious = []
        for i in range(len(predicted_classes)):
            if predicted_classes[i] == 1:
                paths = pathlib.Path(names[i])
                group = paths.parts[-4]
                name = paths.stem
                groupPath = os.path.join(path, "stream/"+group)
                stream = json.load(open(os.path.join(groupPath, "stream.json"), 'r'))["Background_PC"]
                for ua in stream:
                    for file in stream[ua]:
                        if name in file["filename"]:
                            print(ua)
                print(name)
                Malicious.append(names[i])
        print("checking...")
        group_dict = {}
        for i in Malicious:
            paths = pathlib.Path(i)
            # paths = os.path.splitext(i)[0].split("/")
            group = paths.parts[-4]
            name = paths.stem
            if group not in group_dict:
                group_dict[group] = {}
                group_dict[group]["Background_PC"] = []
            tmp_dict = {}
            tmp_dict["is_malicious"] = 1
            tmp_dict["type"] = 0
            tmp_dict["filename"] = name + ".pcap"
            group_dict[group]["Background_PC"].append(tmp_dict)
        val = []
        for i in group_dict:
            streamPath = os.path.join(path, "stream/"+i)
            datasetPath = os.path.join(path, "dataset/"+i)
            retrainPath = os.path.join(path, "retrain/Backgroud_PC/0")
            if not os.path.exists(retrainPath):
                os.mkdir(retrainPath)
            val += StreamManager.validate(group_dict[i], root=streamPath)
            for j in val:
                shutil.copy(os.path.join(datasetPath, "Background_PC/0/"+j[:-4]+"dat"), retrainPath)
        print(val)
        print(len(val)/sum(predicted_classes))
        end = time.time()
        print(end)
        print('Running time: %s Seconds' % (end - start))


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


tf.app.run()
