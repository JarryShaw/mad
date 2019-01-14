#!/usr/bin/env bash

set -x

function cleanup_model() {
    rm -rf /home/traffic/db/apt_model
    tar -xzvf model.tar.gz -C /home/traffic/db
}

function cleanup_retrain() {
    rm -rf /home/traffic/db/apt_retrain
    tar -xzvf retrain.tar.gz -C /home/traffic/db
}

function cleanup_report() {
    rm -rf /home/traffic/db/apt_report
    mkdir -p /home/traffic/db/apt_report
}

function cleanup_dataset() {
    rm -rf ./log/dataset
    mkdir -p ./log/dataset
}

function cleanup_log() {
    > /home/traffic/pcapfile/apt_log.txt
}

function cleanup_db() {
    sql=$( cat ./cleanup.sql ) && \
    docker-compose up --detach mad_db && \
    docker-compose exec mad_db mysql -uroot -pzft13917331612 -e"${sql}"
    docker-compose stop mad_db
}

case $1 in
    all)        cleanup_retrain && cleanup_model && cleanup_report && cleanup_dataset && cleanup_log && cleanup_db ;;
    archives)   cleanup_retrain && cleanup_model ;;
    volumes)    cleanup_report && cleanup_dataset ;;
    dataset)    cleanup_dataset ;;
    retrain)    cleanup_retrain ;;
    report)     cleanup_report ;;
    model)      cleanup_model ;;
    log)        cleanup_log ;;
    db)         cleanup_db ;;
    *)          echo "Invalid option." ;;
esac
