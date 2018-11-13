#!/usr/bin/env bash

set -x

# install requirements
platform=$( uname )
if [[ $platform == "Darwin" ]] ; then
    if [[ -z $( which brew ) ]] ; then
        sudo --set-home python3 -m pip install --upgrade \
            pip \
            wheel \
            setuptools \
            f2format
        returncode=$?
        if [[ $returncode -ne "0" ]] ; then
            exit $returncode
        fi
    else
        brew update && \
        brew install \
            python \
            scons && \
        sudo --set-home python3 -m pip install --upgrade \
            pip \
            wheel \
            setuptools \
            f2format
    fi
elif [[ $platform == "Linux" ]] ; then
    # read -r -a array <<< $( lsb_release -i )
    # dist=${array[-1]}
    if [[ ! -z $( which apt-get ) ]] ; then
        sudo apt-get update && \
        sudo apt-get install -y \
            git \
            libpcap-dev \
            python3 \
            python3-pip \
            scons && \
        sudo --set-home python3 -m pip install --upgrade \
            pip \
            wheel \
            setuptools \
            f2format
    elif [[ ! -z $( which yum ) ]] ; then
        sudo yum update && \
        sudo yum install -y \
            git \
            libpcap-dev \
            python3 \
            python3-pip \
            scons & \
        sudo --set-home python3 -m pip install --upgrade \
            pip \
            wheel \
            setuptools \
            f2format
    else
        sudo --set-home python3 -m pip install --upgrade \
            pip \
            wheel \
            setuptools \
            f2format
        returncode=$?
        if [[ $returncode -ne "0" ]] ; then
            exit $returncode
        fi
    fi
else
    python3 -m pip install --user --upgrade \
        pip \
        wheel \
        setuptools \
        f2format
    returncode=$?
    if [[ $returncode -ne "0" ]] ; then
        exit $returncode
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
    webgraphic \
    www release/

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
