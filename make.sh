#!/usr/bin/env bash

set -x

# allow ** in glob
shopt -s globstar

# prepare source files
mkdir -p apt \
         apt/app \
         apt/gen \
         apt/sql \
         apt/www && \
cp -rf .dockerignore \
       .gitignore \
       AUTHORS.md \
       bootstrap.sh \
       build.sh \
       CHANGELOG.md \
       CONTRIBUTING.md \
       docker-compose.yml \
       docker.sh \
       Dockerfile \
       fingerprint.pickle \
       model.tar.gz \
       retrain.tar.gz apt && \
cp -rf app/init.sh \
       app/mad.py \
       app/make_stream.py \
       app/run_mad.py \
       app/Training.py \
       app/utils.py \
       app/DataLabeler \
       app/fingerprints \
       app/SQLManager \
       app/StreamManager \
       app/webgraphic apt/app && \
cp -rf gen/generate_report.py \
       gen/generator.py \
       gen/init.sh \
       gen/server_map.py \
       gen/SQLManager apt/gen && \
cp -rf sql/MySQL.sql apt/sql && \
cp -rf www/init.sh \
       www/manage.py \
       www/mad \
       www/www apt/www && \
chmod +x apt/**/*.sh && \
sed 's/python_version = "3.6"/python_version = "3.5"/' Pipfile > apt/Pipfile && \
head -2 README.md > apt/README.md && \
echo '<a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/"><img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-nd/4.0/88x31.png" /></a><br />This work is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-nd/4.0/">Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License</a>.' >> apt/README.md && \
tail -n +2 README.md >> apt/README.md
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# de-f-string
pipenv run f2format --encoding UTF-8 --no-archive apt
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# test commit
if [[ $1 =~ "^test$" ]] ; then
    exit 0
fi

# upload to GitLab
cd apt
git pull && \
git add . && \
if [[ -z $1 ]] ; then
    git commit -a -S
else
    git commit -a -S -m "$1"
fi && \
git push
returncode=$?
if [[ $returncode -ne "0" ]] ; then
    exit $returncode
fi

# update maintenance information
cd ..
maintainer changelog && \
maintainer contributor && \
maintainer contributing
ret="$?"
if [[ $ret -ne "0" ]] ; then
    exit $ret
fi

# # update submodules
# git submodule sync && \
# git submodule update && \
# returncode=$?
# if [[ $returncode -ne "0" ]] ; then
#     exit $returncode
# fi

# upload to GitHub
git pull && \
git add . && \
if [[ -z $1 ]] ; then
    git commit -a -S
else
    git commit -a -S -m "$1"
fi && \
git push
