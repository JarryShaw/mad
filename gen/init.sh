#!/usr/bin/env bash

set -x

# change cwd
cd gen

# create link
mkdir -p /mad /mad/report && \
ln -s /mad/report /www/mad/templates/static/report
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# run generator
python3 generate_report.py
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
