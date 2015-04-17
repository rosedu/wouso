#!/bin/bash

# Install operating system dependencies
sudo apt-get install python2.7 python-pip python-django python-dev python-virtualenv libldap2-dev libsasl2-dev libssl-dev

# Enter the sandbox
virtualenv -p python2.7 sandbox
source sandbox/bin/activate

# Install Python dependencies
pip install -r requirements-pip
pip install -r requirements-extra

# Install Django Pyston
curl 'https://pypi.python.org/packages/source/d/django-piston/django-piston-0.2.3.tar.gz' | tar xzf -
cd django-piston-0.2.3; python setup.py install
cd ..; rm -r django-piston-0.2.3

# Create initial settings
cp wouso/settings.py.example wouso/settings.py

# Setup the database
cd wouso
./manage.py wousoctl --setup
cd ..
