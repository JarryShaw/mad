#!/usr/bin/env bash

case $1 in
    docker)
        sudo docker run -v /data/httpdump:/mad/pcap mad --path /mad/pcap
        ;;
    docker-compose)
        sudo docker-compose up --build
        ;;
esac
