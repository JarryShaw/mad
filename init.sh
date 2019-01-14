#!/usr/bin/env bash

set -x

function init_report() {
    mkdir -p /home/traffic/log \
             /home/traffic/log/mad
}

function init_dataset() {
    mkdir -p /home/traffic/db \
             /home/traffic/db/mad
}

function init_db() {
    sql=$( cat sql/MySQL.sql ) && \
    docker-compose up --detach mad_db && \
    docker-compose exec mad_db mysql -uroot -pzft13917331612 -e"${sql}" && \
    docker-compose stop mad_db
}

case $1 in
    all)        init_report && init_dataset && init_db ;;
    volumes)    init_report && init_dataset ;;
    dataset)    init_dataset ;;
    report)     init_report ;;
    db)         init_db ;;
    *)          echo "Invalid option." ;;
esac
