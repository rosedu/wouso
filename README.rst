World of USO
============

World of USO is a quiz game with questions from USO course, 1st year,
ACS.


Installing
----------

1. Install Python >= 2.7 and virtualenv; activate the virtualenv::

    virtualenv -p python2.7 sandbox
    echo '*' > sandbox/.gitignore
    . sandbox/bin/activate

2. Install dependencies::

    (on Ubuntu) sudo apt-get install python-dev libldap2-dev libsasl2-dev
    pip install -r requirements-pip       # optional, the same command with: requirements-extra

3. Install `django-piston` (by hand, because of a weird bug_)::

    curl 'https://pypi.python.org/packages/source/d/django-piston/django-piston-0.2.3.tar.gz' | tar xzf -
    cd django-piston-0.2.3; python setup.py install
    cd ..; rm -r django-piston-0.2.3

.. _bug: https://bitbucket.org/jespern/django-piston/issue/173/attributeerror-module-object-has-no

4. Go to `wouso` folder, run everything from there::

    cd wouso

5. Copy the default settings::

    cp settings.py.example settings.py

6. Create database tables and load initial data::

    ./manage.py wousoctl --setup

7. Run the server::

    ./manage.py runserver
