#!/usr/bin/env bash

set -x

# install requirements
sudo apt-get update && \
sudo apt-get install -y \
    python3 \
    python3-pip
sudo --set-home python3 -m pip install --upgrade \
    pip \
    wheel \
    setuptools \
    f2format

# prepare source files
cp -rf \
    run_mad.py \
    mad.py \
    make_stream.py \
    Training.py \
    DataLabeler \
    fingerprints \
    StreamManager \
    webgraphic release/

# de-f-string
f2format -n release

# build docker
if [[ -z $1 ]] ; then
    docker build -t mad .
else
    docker build -t mad:$1 .
fi
