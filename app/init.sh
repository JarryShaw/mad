#!/usr/bin/env bash

set -x

# change cwd
cd app

# run MAD
# python3 /app/run_mad.py --path /mad/pcap | ts "%Y-%m-%dT%H:%M:%.SZ"
python3 /app/run_mad.py --path /mad/pcap
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi