#!/bin/bash


APPS="config qpool pages"

for app in $APPS
do
    echo "Resetting $app data."
    wouso/manage.py sqlreset $app | wouso/manage.py dbshell
done

echo "Done"

