#!/bin/bash

site_name=sandboxsite
service_name=$site_name

MINIMAL_CHANGE=0
if [ "$MINIMAL_CHANGE" = "1" ]; then
    echo "Minimal change enabled (Ex: update templates )"
    exit 0
fi

chmod 750 ./scripts/*
sudo -u www-data bash ./scripts/syncdb.sh /var/sites/venvs

###
### Install config
###

#htpasswd -cb /var/sites/.htpasswd admin admin
cp -r sysconfig/etc/* /etc/
update-rc.d $service_name defaults 92

###
### Restart services
###

service $service_name stop
sleep 4
service $service_name start

#/etc/init.d/monit restart
#monit monitor all
