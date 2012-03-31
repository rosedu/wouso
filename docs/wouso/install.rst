Install
=======

Obțineți o copie a ultimei versiuni WoUSO
-----------------------------------------

1. Dacă nu aveți deja instalat, instalați git.
2. ``git clone http://git.rosedu.org/down/wouso-django.git``.

Done. Acum aveți sursele WoUSO local, în directorul wouso-django. Dacă
întâmpinați probleme contactați-ne pe lista de discuții.

WoUSO needs
-----------

1. Apache - Server Web

2. mod-wsgi - Modul Apache care permite rularea aplicațiilor Python.

3. Django - Web Framework and more.

4. mysql - Bază de date

5. pip - Înstalare ușoară a dependințelor (pyfacebook, django-facebookconnect)

6. Asigurați-vă ca le aveți instalate. Toate au o documentație foarte
   bună și tutoriale de instalare și configurare.

Dacă sunteți în Ubuntu::

    apt-get install libapache2-mod-wsgi python-django apache2 mysql-server \
        python-ldap python-mysqldb python-pip

Instați pyfacebook and django-facebookconnect::

    pip install -U -r requirements-pip


Opțiuni de configurare
----------------------

Adăugați un alias local în /etc/hosts 127.0.0.1 wouso.local Editați
fișierul wouso.local astfel încât să se potrivească cu setările voastre.
Copiați-l în /etc/apache2/sites-available

Rulați ca root::

    a2ensite wouso.local
    service apache2 reload

Final
-----

Ar trebui să puteți să accesați http://wouso.local. Dacă aveți probleme
la instalare, dați un mesaj pe lista de discuții și cineva vă va ajuta.
