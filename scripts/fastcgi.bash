#!/bin/bash

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
su wouso -c "cd wouso; python manage.py runfcgi --settings=settings maxchildren=10 maxspare=5 minspare=2 method=prefork socket=$LPATH/instance/fcgi.sock pidfile=$LPATH/instance/fcgi.pid umask=000"

echo "done"

