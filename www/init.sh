#!/usr/bin/env bash

set -x

# change cwd
cd www

# setup db
python3 manage.py makemigrations && \
python3 manage.py migrate 2>/dev/null
if [[ $? -ne "0" ]] ; then
    python3 manage.py migrate --fake mad
    returncode=$?
    if [[ $returncode -ne "0" ]] ; then
        exit $returncode
    fi
fi

# startup server
python3 manage.py runserver 0.0.0.0:80
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
