#!/usr/bin/env bash

set -x

# change cwd
cd www

# setup db
python3 manage.py migrate
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# startup server
python3 manage.py runserver 0.0.0.0:80
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
