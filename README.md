# World of USO

World of USO is a quiz game framework. It has been used since 2007 as a
support game for the Introduction to Operating Systems class (USO) by
1st year students at the Faculty of Automatic Control and Computers,
University POLITEHNICA of Bucharest.


## Requirements

The following packages need to be installed::

* python2.7
* python-pip
* python-django
* python-dev
* python-virtualenv
* libldap2-dev
* libsasl2-dev


## Installing WoUSO

0. Fork/Clone the WoUSO repository from GitHub.

1. Browse to the Git repository and activate the virtualenv::

        cd $PATH_TO_WOUSO_REPOSITORY
        virtualenv -p python2.7 sandbox
        echo '*' > sandbox/.gitignore
        . sandbox/bin/activate

    `$PATH_TO_WOUSO_REPOSITORY` is the location of the clone of the WoUSO
repository.

2. Install pip requirements::

        pip install -r requirements-pip       # optional, the same command with: requirements-extra

3. Install `django-piston` (by hand, because of a [weird bug](https://bitbucket.org/jespern/django-piston/issue/173/attributeerror-module-object-has-no))::

        curl 'https://pypi.python.org/packages/source/d/django-piston/django-piston-0.2.3.tar.gz' | tar xzf -
        cd django-piston-0.2.3; python setup.py install
        cd ..; rm -r django-piston-0.2.3


4. Go to `wouso` subfolder, run everything from there::

        cd wouso

5. Copy the default settings::

        cp settings.py.example settings.py

6. Create database tables and load initial data::

        ./manage.py wousoctl --setup

7. Run the server::

        ./manage.py runserver


## Development best practices

After pulling new code from server, run migration:

    ./manage.py migrate


## Hacking on WoUSO Using Vagrant

Make sure you have [Vagrant](http://www.vagrantup.com/), then run
`vagrant up`.

You can now find a deployed version of WoUSO at
[http://localhost:8000](http://localhost:8000).

All the code is shared with the VM, which you can access with `vagrant ssh`.
From there you can find the project files and interact with the django
project as usual.

If you prefer to set up a local copy (not in the VM), read along.
