#!/usr/bin/env bash

set -x

# install requirements
if [[ $( uname ) == "Linux" ]] ; then
    sudo apt-get update && \
    sudo apt-get install -y \
        python3 \
        python3-pip
    sudo --set-home python3 -m pip install --upgrade \
        pip \
        wheel \
        setuptools \
        f2format
fi

# prepare source files
rm -rf release && \
mkdir -p release && \
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
returncode="$?"
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# build docker
if [[ -z $1 ]] ; then
    sudo docker build -t mad .
else
    sudo docker build -t mad:$1 .
fi
