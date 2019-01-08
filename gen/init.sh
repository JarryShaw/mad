#!/usr/bin/env bash

set -x

# change cwd
cd gen

# run generator
# python3 generate_report.py | ts "%Y-%m-%dT%H:%M:%.SZ"
python3 generate_report.py
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
