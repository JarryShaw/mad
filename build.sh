#!/usr/bin/env bash

set -x

# allow ** in glob
shopt -s globstar

# prepare source files
rm -rf build && \
mkdir -p build && \
cp -rf .dockerignore \
       docker-compose.yml \
       Dockerfile \
       model.tar.gz \
       retrain.tar.gz build && \
mkdir -p build/app && \
cp -rf app/init.sh \
       app/mad.py \
       app/make_stream.py \
       app/run_mad.py \
       app/SQLManager.py \
       app/Training.py \
       app/utils.py \
       app/DataLabeler \
       app/fingerprints \
       app/StreamManager \
       app/webgraphic build/app/ && \
mkdir -p build/gen && \
cp -rf gen/generate_report.py \
       gen/init.sh build/gen && \
mkdir -p build/sql && \
cp -rf sql/MySQL.sql build/sql && \
mkdir -p build/www && \
cp -rf www/init.sh \
       www/manage.py \
       www/mad \
       www/www build/www/ && \
chmod +x build/**/*.sh
returncode="$?"
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# de-f-string
pipenv run f2format -n build
returncode="$?"
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# build docker
if [[ -z $1 ]] ; then
    docker build --rm --tag mad build
else
    docker build --rm --tag mad:$1 build
fi

# run docker-compose
cd build
docker-compose up
