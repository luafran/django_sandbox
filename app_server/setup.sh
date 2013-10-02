#!/bin/bash

app_server_user=www-data
app_server_group=www-data

###
### Install OS packages
###

apt-get update
apt-get -y install nginx apache2-utils
#apt-get -y install monit
apt-get -y install python-pip python-mysqldb python-dev python-redis python-pylibmc python-memcache
apt-get -y install libmysqlclient-dev libmemcached-dev libmemcache-dev mysql-client-core-5.5
apt-get -y install zip unzip git make
apt-get -y install libjpeg8-dev libfreetype6-dev openjdk-7-jre
pip install virtualenv virtualenvwrapper

###
### Create directories
###

sites_dir=/var/sites
mkdir -p $sites_dir
chown -R $app_server_user:$app_server_group $sites_dir

log_dir=/var/log/sites
mkdir -p $log_dir
chown -R $app_server_user:$app_server_group $log_dir

run_dir=/var/run/sites
mkdir -p $run_dir
chown -R $app_server_user:$app_server_group $run_dir

###
### Install config
###

#htpasswd -cb /var/sites/.htpasswd admin admin
cp -r sysconfig/etc/* /etc/

###
### Create virtualenv and install requirements
###

requirements_file="./requirements.txt"
venv='django_sandbox'

echo "virtual env setup. using:"
echo "- WORKON_HOME = $WORKON_HOME"
echo "- venv = $venv"
echo "- requirements_file = $requirements_file"

#if [ ! -d $WORKON_HOME ]; then
#    echo "$WORKON_HOME directory does not exists. Creating directory"
#    mkdir $WORKON_HOME
#fi

source /usr/local/bin/virtualenvwrapper.sh
workon $venv > /dev/null 2>&1
if [ $? -ne 0 ]; then
    # virtual env was not created, create it now
    echo "Creating virtual env $venv"
     mkvirtualenv $venv
fi

exit 0

diff $requirements_file $WORKON_HOME/requirements.txt.current
if [ $? -ne 0 ]; then
    pip install -Ur $requirements_file
    cp $requirements_file $WORKON_HOME/requirements.txt.current
else
    echo "requirements.txt did not change. Skipping install of requirements.txt"
fi

# We want venv files to be owned by app_server user and group
chown -R $app_server_user.$app_server_group $sites_dir

###
### Do specific stuff
###

# PIL JPG/PNG SUPPORT
if [ -e /usr/lib/i386-linux-gnu ]; then
    ln -f -s /usr/lib/i386-linux-gnu/libfreetype.so /usr/lib/
    ln -f -s /usr/lib/i386-linux-gnu/libz.so /usr/lib/
    ln -f -s /usr/lib/i386-linux-gnu/libjpeg.so /usr/lib/
fi

if [ -e /usr/lib/x86_64-linux-gnu ]; then
    ln -f -s /usr/lib/x86_64-linux-gnu/libfreetype.so /usr/lib/
    ln -f -s /usr/lib/x86_64-linux-gnu/libz.so /usr/lib/
    ln -f -s /usr/lib/x86_64-linux-gnu/libjpeg.so /usr/lib/
fi

###
### Restart services
###

service nginx restart
#service monit restart
