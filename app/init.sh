#!/usr/bin/env bash

set -x

# change cwd
cd app

# run MAD
#   Sample source: /mad/pcap
#   Rounds interval: 0
#   Sampling intervar: 0
#   Process number: 5
#   MEMLOCK limit: 2M
#   VMEM limit: 2M
#   AS limit: 1G
#   SWAP limit: 2M
#   Validation: yes
#   Develop mode: no
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
