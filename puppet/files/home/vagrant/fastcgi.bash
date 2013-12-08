#!/bin/bash

FCGI_MAXCHILDREN="10"
FCGI_MAXSPARE="5"
FCGI_MINSPARE="2"


if [ ! -d "wouso" ]; then
	echo "Please run in a wouso repo root"
	exit
fi

# stop existing
if [ -f "/tmp/fcgi.pid" ]; then
	kill -9 `cat /tmp/fcgi.pid`
fi

# spawn new fcgi process
su vagrant -c "cd /home/vagrant/wouso/wouso; /home/vagrant/pybox/bin/python manage.py runfcgi maxchildren=$FCGI_MAXCHILDREN maxspare=$FCGI_MAXSPARE minspare=$FCGI_MINSPARE method=prefork daemonize=true socket=/tmp/fcgi.sock pidfile=/tmp/fcgi.pid umask=000"

echo "done"

