#!/usr/bin/env bash

set -x

# prepare source files
rm -rf build && \
mkdir -p build && \
cp app/model.tar.gz \
   app/retrain.tar.gz build && \
mkdir -p build/app && \
cp -rf app/mad.py \
       app/make_stream.py \
       app/run_mad.py \
       app/SQLManager.py \
       app/Training.py \
       app/DataLabeler \
       app/fingerprints \
       app/StreamManager \
       app/webgraphic build/app/ && \
mkdir -p build/www && \
cp -rf www/* build/www/

# de-f-string
pipenv run f2format -n build
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
