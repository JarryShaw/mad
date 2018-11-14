# basic info
FROM ubuntu:16.04
LABEL version="2018.11.14"

# install Python 3 & all requirements
RUN apt-get update && apt-get install -y \
    git \
    libpcap-dev \
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
    PyMySQL \
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
COPY release /app
ADD retrain.tar.gz /usr/local/mad

# entry points
ENTRYPOINT ["python3", "/app/run_mad.py"]
CMD ["--help"]
