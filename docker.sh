#!/usr/bin/env bash

set -x

case $1 in
    docker)         docker build --tag mad .
                    docker run -v /home/traffic/pcapfile:/mad/pcap mad --path /mad/pcap ;;
    docker-compose) docker-compose up --build ;;
esac
