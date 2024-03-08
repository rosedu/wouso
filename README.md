[![Build Status](https://travis-ci.org/rosedu/wouso.svg?branch=master)](https://travis-ci.org/rosedu/wouso)
[![Coverage Status](https://coveralls.io/repos/github/rosedu/wouso/badge.svg?branch=master)](https://coveralls.io/github/rosedu/wouso?branch=master)
[![Code Climate](https://codeclimate.com/github/rosedu/wouso/badges/gpa.svg)](https://codeclimate.com/github/rosedu/wouso)

# World of USO

World of USO is a quiz game framework. It has been used since 2007 as a support game for the Introduction to Operating Systems class (USO) by 1st year students at the Faculty of Automatic Control and Computers, University POLITEHNICA of Bucharest.

## Easy install

On a Mint/Ubuntu/Fedora system run the install script:

```sh
./install.sh
```

During the installation you will be asked to enter an username and password for the administrative user. You will use those to do the first login into World of USO and use full privileges for administrative actions.

If everything installs successfully go to step 9 to start the server.

## Requirements

The following packages need to be installed:

* python2.7
* python-pip
* python-django
* python-dev
* python-virtualenv
* libldap2-dev
* libsasl2-dev
* libssl-dev

On **Debian-based** systems run the command:

```sh
sudo apt-get install python2.7 python-pip python-django python-dev python-virtualenv libldap2-dev libsasl2-dev libssl-dev
```

On **Fedora 22 or higher** systems run the command:

```sh
sudo dnf -y install python-pip python-django python-devel python-virtualenv openldap-devel libgsasl-devel openssl-devel
```

On **Fedora 21 or lower** systems run the command:

```sh
sudo yum -y install python-pip python-django python-devel python-virtualenv openldap-devel libgsasl-devel openssl-devel
```

Optional packages (in case of MySQL support):
* mysql-server
* mysql-client
* libmysqlclient-dev


## Installing WoUSO

1. Fork/Clone the WoUSO repository from GitHub.

2. Browse to the Git repository and activate the virtualenv:

```sh
cd $PATH_TO_WOUSO_REPOSITORY
virtualenv -p python2.7 sandbox
source sandbox/bin/activate
```

`$PATH_TO_WOUSO_REPOSITORY` is the location of the clone of the WoUSO repository.

You'll notice it works as you get a prompt update: the `(sandbox)` string is prefixed to the prompt. Something like:

```sh
(sandbox)wouso@wouso-dev:~/wouso.git$
```

In case you do something wrong in the virtualenv, you may exit it using

```sh
deactivate
```

and you may then remove the `sandbox` folder:

```sh
rm -r sandbox
```

3. Install pip requirements while in the `$PATH_TO_WOUSO_REPOSITORY` folder:

```sh
pip install -r requirements-pip
pip install -r requirements-extra
```

4. Install `django-piston` for WoUSO REST API (by hand, because of a [weird bug](https://bitbucket.org/jespern/django-piston/issue/173/attributeerror-module-object-has-no)):

```sh
curl 'https://pypi.python.org/packages/source/d/django-piston/django-piston-0.2.3.tar.gz' | tar xzf -
cd django-piston-0.2.3; python setup.py install
cd ..; rm -r django-piston-0.2.3
```


5. Go to `wouso` subfolder, run everything from there:

```sh
cd wouso/
```

6. Create initial settings. First make a copy of example settings:

```sh
cp settings.py.example settings.py
```

and edit the new file (`settings.py`). You may want to update the `DATABASES` setting (see next step).

7. (optional) In case you want to use a MySQL database, you must have the MySQL server and client packages installed. For MySQL support in Python you can use `pip`:

```sh
pip install MySQL-python
```

Create the database and use and use appropriate settings. For example, one would issue these commands in the MySQL client prompt to create a database:

```sql
create database wouso default character set utf8 default collate utf8_general_ci;
create user 'wouso'@'localhost' identified by 'some_pass';
grant all privileges on wouso.* to 'wouso'@'localhost';
flush privileges;
```

The appropriate database configuration in the `settings.py` file will then look like this:

```py
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
```

8. Create database tables and load initial data:

```sh
./manage.py wousoctl --setup
```

You will be asked to enter an username and password for the administrative user. You will use those to do the first login into World of USO and use full privileges for administrative actions.

9. Run the server:

```sh
./manage.py runserver
```

By default the server listens for connections on localhost port 8000. In case you want the server to listen on all interfaces, run

```sh
./manage.py runserver 0.0.0.0:8000
```

You can now point your browser to an URL such as `http://localhost:8000` or `http://<IP>:8000/` (where `<IP>` is the IP address of the host where you installed World of USO).


If you want to leave the virtualenv, run

```sh
deactivate
```


### Development Virtual Machine

In case you run into issues when installing/configuring World of USO or you just want a quick development/testing environment, you can grab the [development VM](https://github.com/rosedu/wouso/wiki/Development-VM).


### Using Vagrant

You may create a development environment using [Vagrant](http://www.vagrantup.com/). Make sure Vagrant is installed, then run

```sh
vagrant up
```

You can now find a deployed version of WoUSO at [http://localhost:8000](http://localhost:8000).

All code is shared with the VM, which you can access using

```sh
vagrant ssh
```

From there you can find the project files and interact with the django project as usual.
This also generated a superuser `admin:admin`.


## Development Best Practices

After pulling new code from server, while in sandbox mode, update the database schema by running the migration action:

```sh
./manage.py migrate
```

In case of issues, you may need to update the pip packages, by running the commands below while in the repository:

```sh
pip install -r requirements-pip
pip install -r requirements-extra
```

## Troubleshooting

### TemplateDoesNotExist at /admin/index.html

```sh
rsync -a -v --ignore-existing src dst
```

Where:
* **`src`** is `/yourvirtualenv/django/` (i.e. `$PATH_TO_WOUSO_REPOSITORY/sandbox/django/`)
* **`dst`** is `/yourvirtualenv/lib/python2.7/site-packages/django/` (i.e. `$PATH_TO_WOUSO_REPOSITORY/sandbox/lib/python2.7/site-packages/django/`)
