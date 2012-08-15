#!/bin/bash

FCGI_MAXCHILDREN="10"
FCGI_MAXSPARE="5"
FCGI_MINSPARE="2"


if [ ! -d "wouso" ]; then
	echo "Please run in a wouso repo root"
	exit
fi

LPATH=`pwd`

# create instance dir
su wouso -c "mkdir -p $LPATH/instance"

# stop existing
if [ -f "$LPATH/instance/fcgi.pid" ]; then
	kill -9 `cat $LPATH/instance/fcgi.pid`
fi

# spawn new fcgi process
su wouso -c "cd wouso; python manage.py runfcgi --settings=settings maxchildren=$FCGI_MAXCHILDREN maxspare=$FCGI_MAXSPARE minspare=$FCGI_MINSPARE method=prefork socket=$LPATH/instance/fcgi.sock pidfile=$LPATH/instance/fcgi.pid umask=000"

echo "done"

