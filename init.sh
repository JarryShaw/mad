#!/usr/bin/env bash

set -x

function init_model() {
    mkdir -p /home/traffic/db && \
    tar -xzvf model.tar.gz -C /home/traffic/db
}

function init_retrain() {
    mkdir -p /home/traffic/db && \
    tar -xzvf retrain.tar.gz -C /home/traffic/db
}

function init_report() {
    mkdir -p /home/traffic/db \
             /home/traffic/db/apt_report
}

function init_dataset() {
    mkdir -p ./log \
             ./log/dataset
}

function init_db() {
    sql=$( cat sql/MySQL.sql ) && \
    docker-compose up --detach mad_db && \
    docker-compose exec mad_db mysql -uroot -pzft13917331612 -e"${sql}"
    docker-compose stop mad_db
}

case $1 in
    all)        init_retrain && init_model && init_report && init_dataset && init_db ;;
    archives)   init_retrain && init_model ;;
    volumes)    init_report && init_dataset ;;
    dataset)    init_dataset ;;
    retrain)    init_retrain ;;
    report)     init_report ;;
    model)      init_model ;;
    db)         init_db ;;
    *)          echo "Invalid option." ;;
esac
