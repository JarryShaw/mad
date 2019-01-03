#!/usr/bin/env bash

set -x

# change cwd
cd app

# link logs
mkdir -p /mad /mad/pcap && \
touch /mad/mad.log && \
ln /mad/mad.log /mad/pcap/apt_log.txt
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# run MAD
# python3 /app/run_mad.py --path /mad/pcap | ts "%Y-%m-%dT%H:%M:%.SZ"
cpulimit --limit=50 -- python3 /app/run_mad.py --path /mad/pcap
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
