#!/bin/bash

# Retrieve distribution and release version
DISTRIBUTION=$(lsb_release -i 2> /dev/null | cut -d ':' -f 2 | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
RELEASE=$(lsb_release -r 2> /dev/null | cut -d ':' -f 2 | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
ERR_MSG="Unsupported Linux distribution, please install manually.
See https://github.com/rosedu/wouso#installing-wouso for details.
Aborting..."

if [ -z "$DISTRIBUTION" -o -z "$RELEASE" ]; then
    echo -e "$ERR_MSG"; exit 1
fi

# Install dependencies
if [ "$DISTRIBUTION" == "Ubuntu" -o "$DISTRIBUTION" == "LinuxMint" ]; then
    sudo apt-get install python2.7 python-pip python-django python-dev python-virtualenv libldap2-dev libsasl2-dev libssl-dev
elif [ "$DISTRIBUTION" == "Fedora" ]; then
    if [ "$RELEASE" -ge 22 ]; then
        sudo dnf -y install python-pip python-django python-devel python-virtualenv openldap-devel libgsasl-devel openssl-devel
    else
        sudo yum -y install python-pip python-django python-devel python-virtualenv openldap-devel libgsasl-devel openssl-devel
    fi
else
    echo -e "$ERR_MSG"; exit 1
fi

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
