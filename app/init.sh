#!/usr/bin/env bash

set -x

# change cwd
cd app

# run MAD
#   Sample source: /mad/pcap
#   Rounds interval: 0s
#   Sampling intervar: 0
#   Process number: 15
#   MEMLOCK limit: unlimited
#   VMEM limit: unlimited
#   AS limit: unlimited
#   SWAP limit: unlimited
#   Validation: yes
#   Develop mode: no
#   Validation ratio: 10%
python3 run_mad.py --path /mad/pcap \
# python3 -m cProfile -o del.out run_mad.py --path /mad/pcap \
                   --wait-timeout=0 \
                   --sampling-interval=0 \
                   --process=15 \
                   --memlock=-1 \
                   --vmem=-1 \
                   --address-space=-1 \
                   --swap=-1 \
                   --validate-ratio=10
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
