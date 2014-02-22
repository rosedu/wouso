# World of USO

World of USO is a quiz game framework. It has been used since 2007 as a
support game for the Introduction to Operating Systems class (USO) by
1st year students at the Faculty of Automatic Control and Computers,
University POLITEHNICA of Bucharest.


## Requirements

The following packages need to be installed:

* python2.7
* python-pip
* python-django
* python-dev
* python-virtualenv
* libldap2-dev
* libsasl2-dev

On a Debian-based system run the command:

    sudo apt-get install python2.7 python-pip python-django python-dev python-virtualenv libldap2-dev libsasl2-dev

In case of MySQL support:

    sudo apt-get install mysql-server mysql-client libmysqlclient-dev


## Installing WoUSO

0. Fork/Clone the WoUSO repository from GitHub.

1. Browse to the Git repository and activate the virtualenv:

        cd $PATH_TO_WOUSO_REPOSITORY
        virtualenv -p python2.7 sandbox
        echo '*' > sandbox/.gitignore
        . sandbox/bin/activate

    `$PATH_TO_WOUSO_REPOSITORY` is the location of the clone of the WoUSO
repository.

2. Install pip requirements while in the `$PATH_TO_WOUSO_REPOSITORY` folder:

        pip install -r requirements-pip
        pip install -r requirements-extra

3. Install `django-piston` for WoUSO REST API (by hand, because of a [weird bug](https://bitbucket.org/jespern/django-piston/issue/173/attributeerror-module-object-has-no)):

        curl 'https://pypi.python.org/packages/source/d/django-piston/django-piston-0.2.3.tar.gz' | tar xzf -
        cd django-piston-0.2.3; python setup.py install
        cd ..; rm -r django-piston-0.2.3


4. Go to `wouso` subfolder, run everything from there:

        cd wouso/

5. Create initial settings. First make a copy of example settings:

        cp settings.py.example settings.py

    and edit the new file (`settings.py`). You may want to update the `DATABASES` setting.

6. Updating Database Settings for MySQL

    In case you want to use a MySQL database, you must have the MySQL server and client packages installed. MySQL support in Python is required you can use `pip`:

        pip install MySQL-python

    Create the database and use and use appropriate settings. For example, one would issue these commands in the MySQL client prompt to create a database:

        create database wouso default character set utf8 default collate utf8_general_ci;
        create user 'wouso'@'localhost' identified by 'some_pass';
        grant all privileges on wouso.* to 'wouso'@'localhost';

    The appropriate database configuration in the `settings.py` file will then look like this:

        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.mysql',
                'NAME': 'wouso',
                'USER': 'wouso',
                'PASSWORD': 'wouso',
                'HOST': 'localhost',
                'PORT': '',
            }
        }

6. Create database tables and load initial data:

        ./manage.py wousoctl --setup

7. Run the server:

        ./manage.py runserver

    By default the server listens for connections on localhost port 8000. In case you want the server to listen on all interfaces, run

        ./manage.py runserver 0.0.0.0:8000


If you want to leave the virtualenv, run

        deactivate


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
