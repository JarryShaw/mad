#!/usr/bin/env bash

set -x

# cleanup volumes
rm -rf  /home/traffic/db/mad \
        /home/traffic/log/mad && \
mkdir -p /home/traffic/db/mad \
         /home/traffic/log/mad

# empty log
> /home/traffic/pcapfile/apt_log.txt

# reset database
mysql -uroot -pzft13917331612 -eclean.sql
