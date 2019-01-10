#!/usr/bin/env bash

set -x

# change cwd
cd gen

# run generator
#   Process number: 3
#   Sleep interval: 5m
#   API token: 6JJ0qCCNHzv6iLsPvUPQNst0Dpbh87io
python3 generate_report.py --process=3 \
                           --interval=300 \
                           --token='6JJ0qCCNHzv6iLsPvUPQNst0Dpbh87io'
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi
