#!/usr/bin/env bash

set -x

# prepare source files
mkdir -p apt apt/app apt/www && \
cp -rf .dockerignore \
       .gitignore \
       bootstrap.sh \
       build.sh \
       Dockerfile \
       LICENSE \
       model.tar.gz \
       retrain.tar.gz \
       README.md apt && \
cp -rf app/mad.py \
       app/make_stream.py \
       app/run_mad.py \
       app/SQLManager.py \
       app/Training.py \
       app/utils.py \
       app/DataLabeler \
       app/fingerprints \
       app/StreamManager \
       app/webgraphic apt/app && \
cp -rf www/* apt/www && \
sed 's/python_version = "3.6"/python_version = "3.5"/' Pipfile > apt/Pipfile
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# de-f-string
pipenv run f2format -n apt
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# upload to GitLab
cd apt
git pull && \
git add . && \
if [[ -z $1 ]] ; then
    git commit -a -S
else
    git commit -a -S -m "$1"
fi && \
git push

# update maintenance information
cd ..
maintainer changelog && \
maintainer contributor && \
maintainer contributing
ret="$?"
if [[ $ret -ne "0" ]] ; then
    exit $ret
fi

# upload to GitHub
git pull && \
git add . && \
if [[ -z $1 ]] ; then
    git commit -a -S
else
    git commit -a -S -m "$1"
fi && \
git push
