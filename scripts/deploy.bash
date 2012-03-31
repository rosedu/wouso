#!/bin/bash

if [ ! -d 'wouso' ]; then
	echo "Please run in a wouso repo root!";
	exit -1;
fi

# Update code
git pull --rebase

LDATE=`git show --format="%ai" | tr -d "-" | tr -d ' ' | tr -d ":" | cut -d '+' -f 1 | head -n 1`
VER=`grep WOUSO_VERSION wouso/settings.py | head -n 1`
VER=$VER" + '~"$LDATE"'"

echo "Current version: "$VER

grep -v WOUSO_VERSION wouso/localsettings.py > tmp
echo $VER >> tmp
mv tmp wouso/localsettings.py

echo "Done!"

