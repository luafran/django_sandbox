#!/bin/bash
scriptname=`basename $0`

if [ $# -ne 5 ]; then
    echo "ERROR: invalid parameters"
    echo "Usage: $scriptname venvs_dir user group pid_file log_file"
    exit 1
fi

venvs_dir=$1
user=$2
group=$3
pid_file=$4
log_file=$5

#WORKON_HOME=$venvs_dir
venv=django_sandbox
source /usr/local/bin/virtualenvwrapper.sh
workon $venv

unicorn_cmd=$WORKON_HOME/$venv/bin/gunicorn

num_cpu=`cat /proc/cpuinfo |grep processor|wc -l`
num_workers=$[ ($num_cpu*2)  +  1 ]


log_dir=$(dirname $log_file)
if [ ! -d $log_dir ]; then
    echo "Log dir $log_dir not found. Aborting"
    exit 1
fi

run_dir=$(dirname $pid_file)
if [ ! -d $run_dir ]; then
    echo "Run dir $run_dir not found. Aborting"
    exit 1
fi

$unicorn_cmd -w $num_workers \
    --user=$user --group=$group --log-level=error \
    --worker-connections=1000 --timeout=150 --log-file=$log_file --pid=$pid_file sandboxsite.wsgi:application 2>> $log_file  &

chown $user:$group $log_file

#sometimes it wont load (change for a for and ps later )
sleep 4
