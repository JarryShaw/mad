#!/usr/bin/env bash

set -x

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
