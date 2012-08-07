#!/bin/bash
# Basic level editor, able to reset, load and save a level definition file
# A level definition file is a JSON representation of the database.
#
echo "WARNING: This script is deprecated, use ./manage.py wousoctl instead"

MANAGE_SCRIPT=./manage.py

if [ $# == 0 ]; then
	echo "Usage: $0 [reset|load|save] <file>"
	exit -1
fi

if [ "$1" == "reset" ]; then
	# Resetting everything to a plain default
	$MANAGE_SCRIPT sqlreset magic scoring config pages | ./manage.py dbshell
    # Run default-setup
	bash default_setup.bash
	exit 0
fi

if [ $# -lt 2 ]; then
	echo "Please specify file to load/save from"
	exit -2
fi

if [ "$1" == "load" ]; then
	$MANAGE_SCRIPT loaddata $2
	exit 0
fi

if [ "$1" == "save" ]; then
	$MANAGE_SCRIPT dumpdata --indent=1 magic scoring.coin scoring.formula config pages > $2
	exit 0
fi
