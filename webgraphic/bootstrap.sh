#!/usr/bin/env bash

# install requirements
sudo apt-get update && \
sudo apt-get install -y \
    git \
    libpcap-dev \
    python3 \
    python3-pip \
    scons
sudo --set-home python3 -m pip install --upgrade \
    pip \
    wheel \
    setuptools \
    pipenv

# prepare Pipenv
pipenv --python 3.5 && \
pipenv install --dev

# build pkt2flow
git clone https://github.com/caesar0301/pkt2flow.git && \
cd ./pkt2flow && \
sudo scons --prefix=/usr/local install && \
cd .. && \
rm -rf ./pkt2flow
