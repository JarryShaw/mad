#!/usr/bin/env bash

# install requirements
platform=$( uname )
if [[ $platform == "Darwin" ]] ; then
    if [[ -z $( which brew ) ]] ; then
        exit 1
    fi
    brew update && \
    brew install \
        python \
        scons && \
    sudo --set-home python3 -m pip install --upgrade \
        pip \
        wheel \
        setuptools \
        pipenv
elif [[ $platform == "Linux" ]] ; then
    read -r -a array <<< $( lsb_release -i )
    dist=${array[-1]}
    if [[ $dist -eq "Ubuntu" ]] ; then
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
            pipenv
    elif [[ $dist -eq "CentOS" ]] ; then
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
            pipenv
    else
        exit 1
    fi
fi

# prepare Pipenv
pipenv install --dev

# build pkt2flow
git clone https://github.com/caesar0301/pkt2flow.git && \
cd ./pkt2flow && \
sudo scons --prefix=/usr/local install && \
cd .. && \
rm -rf ./pkt2flow
