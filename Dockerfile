# basic info
FROM library/ubuntu:16.04
LABEL version "2019.02.11"

# set up environment variables
ENV LANG "C.UTF-8"
ENV LC_ALL "C.UTF-8"
ENV PYTHONIOENCODING "UTF-8"

# install Python 3 & all requirements
RUN apt-get update \
 && apt-get install -y \
       git \
       libpcap-dev \
       python3 \
       python3-pip \
       scons \
       tzdata \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# build dependency
RUN git clone https://github.com/caesar0301/pkt2flow.git /tmp/pkt2flow \
 && cd /tmp/pkt2flow \
 && scons --prefix=/usr/local install \
 && cd .. \
 && rm -rf /tmp/pkt2flow \
 && apt remove -y scons

# get wait-for-it
RUN git clone https://github.com/vishnubob/wait-for-it.git /tmp/wait-for-it \
 && cd /tmp/wait-for-it \
 && cp wait-for-it.sh /usr/local/bin/wait-for-it \
 && chmod +x /usr/local/bin/wait-for-it \
 && rm -rf /tmp/wait-for-it \
 && apt remove -y git

# set up timezone
RUN echo 'Asia/Shanghai' > /etc/timezone \
 && rm -f /etc/localtime \
 && ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
 && dpkg-reconfigure -f noninteractive tzdata \
 && apt autoremove -y

# install Python packages & dependencies
COPY lib/python /tmp/python
RUN python3 -m pip install --no-deps --cache-dir=/tmp/pip \
       /tmp/python/pip-* \
       /tmp/python/setuptools-* \
       /tmp/python/wheel-* \
 && rm -rf /tmp/python/pip-* \
           /tmp/python/setuptools-* \
           /tmp/python/wheel-* \
 && python3 -m pip install --no-deps --cache-dir=/tmp/pip \
       /tmp/python/* \
 && rm -rf /tmp/pip /tmp/python

# copy source files
COPY app /app
COPY gen /gen
COPY www /www

# entry points
ENTRYPOINT ["python3", "/app/run_mad.py"]
CMD ["--help"]
