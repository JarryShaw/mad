#!/usr/bin/env bash

set -x

function cleanup_report() {
    rm -rf /home/traffic/log/mad && \
    mkdir -p /home/traffic/log/mad
}

function cleanup_dataset() {
    rm -rf /home/traffic/db/mad && \
    mkdir -p /home/traffic/db/mad
}

function cleanup_log() {
    > /home/traffic/pcapfile/apt_log.txt
}

function cleanup_db() {
    sql=$( cat cleanup.sql ) && \
    docker-compose up --detach mad_db && \
    docker-compose exec mad_db mysql -uroot -pzft13917331612 -e"${sql}" && \
    docker-compose stop mad_db
}

case $1 in
    all)        cleanup_report && cleanup_dataset && cleanup_log && cleanup_db ;;
    volumes)    cleanup_report && cleanup_dataset ;;
    dataset)    cleanup_dataset ;;
    report)     cleanup_report ;;
    log)        cleanup_log ;;
    db)         cleanup_db ;;
esac

# # cleanup volumes
# rm -rf  /home/traffic/db/mad \
#         /home/traffic/log/mad && \
# mkdir -p /home/traffic/db/mad \
#          /home/traffic/log/mad

# # empty log
# > /home/traffic/pcapfile/apt_log.txt

# # reset database
# sql=$( cat clean.sql ) && \
# docker-compose up mad_db && \
# docker-compose exec mad_db mysql -uroot -pzft13917331612 -e"${sql}"
