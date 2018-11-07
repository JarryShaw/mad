#!/usr/bin/env bash

set -x

# upload to GitHub
git pull
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
git add .
if [[ -z $1 ]] ; then
    git commit -a
else
    git commit -a -m "$1"
fi
git push

# prepare source files
mkdir -p apt && \
cp -rf \
    .dockerignore \
    .gitignore \
    bootstrap.sh \
    Dockerfile \
    Pipfile \
    Pipfile.lock \
    README.md \
    retrain.tar.gz \
    run_mad.py \
    mad.py \
    make_stream.py \
    Training.py \
    DataLabeler \
    fingerprints \
    StreamManager \
    webgraphic apt/

# de-f-string
f2format -n apt
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# upload to GitLab
cd apt
git pull
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
git add .
if [[ -z $1 ]] ; then
    git commit -a
else
    git commit -a -m "$1"
fi
git push
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
