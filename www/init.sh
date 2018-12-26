#!/usr/bin/env bash

set -x

# change cwd
cd www

# setup db
python3 manage.py migrate

# startup server
python3 manage.py runserver 0.0.0.0:80
