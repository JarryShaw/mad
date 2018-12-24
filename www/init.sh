#!/usr/bin/env bash

python3 /www/manage.py migrate
python3 /www/manage.py runserver 0.0.0.0:80
