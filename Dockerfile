# basic info
FROM ubuntu:16.04
LABEL version="2018.12.05"

# install Python 3 & all requirements
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    libpcap-dev \
    libffi-dev \
    libssl-dev \
    python3 \
    python3-pip \
    scons \
 && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade --cache-dir=/tmp/pip \
    pip \
    wheel \
    setuptools \
    Django \
    dpkt \
    geocoder \
    peewee \
    pymysql \
    requests\
    scapy \
    tensorflow \
    user-agents \
 && rm -rf /tmp/pip

# build dependency
RUN git clone https://github.com/caesar0301/pkt2flow.git /tmp/pkt2flow \
 && cd /tmp/pkt2flow \
 && scons --prefix=/usr/local install \
 && cd .. \
 && rm -rf /tmp/pkt2flow

# copy source files and archives
COPY build/app /app
COPY build/www /www
ADD build/model.tar.gz /mad
ADD build/retrain.tar.gz /mad

# entry points
ENTRYPOINT ["python3", "/app/run_mad.py"]
CMD ["--help"]
