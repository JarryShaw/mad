#!/usr/bin/env bash

set -x

# prepare source files
mkdir -p apt && \
cp -rf .dockerignore \
       .gitignore \
       bootstrap.sh \
       build.sh \
       Dockerfile \
       LICENSE \
       README.md \
       app/mad.py \
       app/make_stream.py \
       app/retrain.tar.gz \
       app/Backgroud_PC_Model_20180515_httpheader.tar \
       app/run_mad.py \
       app/Training.py \
       app/DataLabeler \
       app/fingerprints \
       app/StreamManager \
       app/webgraphic \
       www apt/ && \
sed 's/python_version = "3.6"/python_version = "3.5"/' Pipfile > apt/Pipfile
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# de-f-string
f2format -n apt
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# upload to GitLab
cd apt && \
git pull && \
git add . && \
if [[ -z $1 ]] ; then
    git commit -a -S
else
    git commit -a -S -m "$1"
fi && \
git push
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# upload to GitHub
cd .. && \
git pull && \
git add . && \
if [[ -z $1 ]] ; then
    git commit -a -S
else
    git commit -a -S -m "$1"
fi && \
git push
