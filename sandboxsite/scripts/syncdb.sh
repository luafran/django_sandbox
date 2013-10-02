#!/bin/bash
scriptname=`basename $0`

if [ $# -ne 1 ]; then
    echo "ERROR: invalid parameters"
    echo "Usage: $scriptname venvs_dir"
    exit 1
fi

venvs_dir=$1

WORKON_HOME=$venvs_dir
venv=web
source /usr/local/bin/virtualenvwrapper.sh
workon $venv

python ./manage.py syncdb --noinput
python ./manage.py createcachetable cache_table
#python ./manage.py migrate
