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

    pip install -r requirements-pip       # optional, the same command with: requirements-extra

3. Go to `wouso` folder, run everything from there::

    cd wouso

4. Copy the default settings::

    cp settings.py.example settings.py

5. Create database tables and load initial data::

    ./manage.py wousoctl --setup

6. Run the server::

    ./manage.py runserver
