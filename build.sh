#!/usr/bin/env bash

set -x

# allow ** in glob
shopt -s globstar

# update version tag
version=$( python -c "print('\"%s\"' % __import__('datetime').date.today().strftime('%Y.%m.%d'))" )
sed "s/LABEL version.*/LABEL version ${version}/" Dockerfile > Dockerfile.tmp
mv Dockerfile.tmp Dockerfile

# prepare source files
rm -rf build && \
mkdir -p build && \
cp -rf .dockerignore \
       cleanup.sh \
       cleanup.sql \
       docker-compose.yml \
       Dockerfile \
       init.sh build && \
mkdir -p build/app && \
cp -rf app/init.sh \
       app/mad.py \
       app/make_stream.py \
       app/run_mad.py \
       app/Training.py \
       app/jsonutil.py \
       app/DataLabeler \
       app/fingerprints \
       app/SQLManager \
       app/StreamManager \
       app/webgraphic build/app/ && \
mkdir -p build/gen && \
cp -rf gen/generate_report.py \
       gen/generator.py \
       gen/init.sh \
       gen/jsonutil.py \
       gen/server_map.py \
       gen/SQLManager build/gen && \
mkdir -p build/lib && \
cp -rf lib/archive \
       lib/python build/lib && \
mkdir -p build/sql && \
cp -rf sql/MySQL.sql build/sql && \
mkdir -p build/www && \
cp -rf www/init.sh \
       www/manage.py \
       www/mad \
       www/www build/www/ && \
chmod +x build/**/*.sh
returncode="$?"
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# de-f-string
pipenv run f2format --encoding UTF-8 --no-archive build
returncode="$?"
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# build docker
if [[ -z $1 ]] ; then
    docker build --rm --tag mad build
else
    docker build --rm --tag mad:$1 build
fi
returncode="$?"
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# run docker-compose
if [[ $1 =~ ^build$ ]] ; then
    echo "Build only; not to start up docker-compose."
else
    cd build
    bash init.sh volumes
    docker-compose up
fi
