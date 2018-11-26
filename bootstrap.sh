#!/usr/bin/env bash

set -x

# install requirements
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
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# prepare Pipenv
pipenv install --dev
returncode="$?"
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# clone dist env
git clone http://gitlab.opensdns.com/contest/apt.git apt && \
cd apt && \
git config user.name zoufutai && \
git config user.email zoufutai@sjtu.edu.cn && \
cd ..

# build pkt2flow
if [[ -z $1 ]] ; then
    git clone https://github.com/caesar0301/pkt2flow.git && \
    cd ./pkt2flow && \
    sudo scons --prefix=/usr/local install && \
    cd .. && \
    rm -rf ./pkt2flow
else
    echo "not to build pkt2flow"
fi
