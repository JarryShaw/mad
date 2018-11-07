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
            pipenv
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
            pipenv
    fi
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
        sudo --set-home python3 -m pip install --upgrade \
            pip \
            wheel \
            setuptools \
            pipenv
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
        pipenv
    returncode=$?
    if [[ $returncode -ne "0" ]] ; then
        exit $returncode
    fi
fi

# prepare Pipenv
pipenv install --dev

# clone dist env
rm -rf apt
git clone http://gitlab.opensdns.com/apt.git apt && \
cd apt && \
git config user.name zoufutai && \
git cnofig user.email zoufutai@sjtu.edu.cn && \
cd ..

# build pkt2flow
if [[ -z $1 ]] ; then
    git clone https://github.com/caesar0301/pkt2flow.git && \
    cd ./pkt2flow && \
    sudo scons --prefix=/usr/local install && \
    cd .. && \
    rm -rf ./pkt2flow
else
    echo "not to make pkt2flow"
fi
