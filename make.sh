#!/usr/bin/env bash

set -x

# install requirements
platform=$( uname )
if [[ $platform == "Darwin" ]] ; then
    if [[ -z $( which brew ) ]] ; then
        exit 1
    fi
    brew update && \
    brew install python && \
    sudo --set-home python3 -m pip install --upgrade \
        pip \
        wheel \
        setuptools \
        f2format
elif [[ $platform == "Linux" ]] ; then
    read -r -a array <<< $( lsb_release -i )
    dist=${array[-1]}
    if [[ $dist -eq "Ubuntu" ]] ; then
        sudo apt-get update && \
        sudo apt-get install -y \
            python3 \
            python3-pip && \
        sudo --set-home python3 -m pip install --upgrade \
            pip \
            wheel \
            setuptools \
            f2format
    elif [[ $dist -eq "CentOS" ]] ; then
        sudo yum update && \
        sudo yum install -y \
            python36
            python36-pip & \
        sudo --set-home python3 -m pip install --upgrade \
            pip \
            wheel \
            setuptools \
            f2format
    else
        exit 1
    fi
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
