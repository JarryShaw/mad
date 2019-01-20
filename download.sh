#!/usr/bin/env bash

set -x

mkdir -p lib lib/python

python3.5 -m pip download --requirement=requirements.txt \
                          --platform=manylinux1_x86_64 \
                          --python-version=35 \
                          --implementation=cp \
                          --dest=lib/python \
                          --no-deps
