#!/usr/bin/env bash

set -x

# change cwd
cd app

# run MAD
# python3 run_mad.py --path /mad/pcap | ts "%Y-%m-%dT%H:%M:%.SZ"
python3 run_mad.py --path /mad/pcap \
                   --wait-timeout=0 \
                   --sampling-interval=0 \
                   --process=5 \
                   --memlock=2097152 \
                   --vmem=2097152 \
                   --address-space=1073741824 \
                   --swap=2097152
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
