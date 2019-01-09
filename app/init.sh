#!/usr/bin/env bash

set -x

# change cwd
cd app

# run MAD
#   Sample source: /mad/pcap
#   Rounds interval: 0
#   Sampling intervar: 0
#   Process number: 5
#   MEMLOCK limit: 2G
#   VMEM limit: 1G
#   AS limit: 10G
#   SWAP limit: 2M
#   Validation: yes
#   Develop mode: no
python3 run_mad.py --path /mad/pcap \
                   --wait-timeout=0 \
                   --sampling-interval=0 \
                   --process=5 \
                   --memlock=2147483648 \
                   --vmem=1073741824 \
                   --address-space=10737418240 \
                   --swap=2097152
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
