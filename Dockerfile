# basic info
FROM ubuntu:16.04
LABEL version="2018.12.20"

# set up environment variables
ENV LANG "C.UTF-8"
ENV LC_ALL "C.UTF-8"
ENV PYTHONIOENCODING "UTF-8"

# install Python 3 & all requirements
RUN apt-get update \
 && apt-get install -y \
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
 && python3 -m pip install --upgrade --cache-dir=/tmp/pip \
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

# get wait-for-it
RUN curl https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh > /usr/local/bin/wait-for-it \
 && chmod +x /usr/local/bin/wait-for-it.sh

# copy source files and archives
ADD model.tar.gz /mad
ADD model.tar.gz /mad
COPY app /app
COPY www /www

# entry points
ENTRYPOINT ["python3", "/app/run_mad.py"]
CMD ["--help"]
