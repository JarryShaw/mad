#!/usr/bin/env bash

set -x

# change cwd
cd app

# run MAD
# python3 run_mad.py --path /mad/pcap | ts "%Y-%m-%dT%H:%M:%.SZ"
python3 run_mad.py --path /mad/pcap \
                   --process=5 \
                   --memlock=1000000000 \
                   --vmem=1000000000
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
