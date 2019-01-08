#!/usr/bin/env bash

set -x

# change cwd
cd www

# create link
mkdir -p /mad /mad/report && \
ln -s /mad/report /www/mad/templates/static/report
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# setup db
# python3 manage.py migrate | ts "%Y-%m-%dT%H:%M:%.SZ"
python3 manage.py makemigrations && \
python3 manage.py migrate
if [[ $? -ne "0" ]] ; then
    python3 manage.py migrate --fake mad
    returncode=$?
    if [[ $returncode -ne "0" ]] ; then
        exit $returncode
    fi
fi

# startup server
# python3 manage.py runserver 0.0.0.0:80 | ts "%Y-%m-%dT%H:%M:%.SZ"
python3 manage.py runserver 0.0.0.0:80
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
