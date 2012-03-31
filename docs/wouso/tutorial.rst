Tutorial
========

Dacă ai intenția să lucrezi la WoUSO sunt mai mulți pași pe care dacă îi
respecți, viața ta va fi mai ușoară.

1) Înscrie-te pe lista de discuții. Aici se discută absolut totul legat
   de dezvoltarea jocului. Poți propune idei sau ne poți spune dacă vrei
   să ne ajuți.

2) Am considerat util să îți oferim un punct de plecare în
   python/django. Dacă ești familiar cu acestea poți să mergi direct la
   instalare

Learning Python
---------------

Dacă nu îl aveți instalat, instalați Python. Ar trebui să știți să
faceți asta.

Primii pași
~~~~~~~~~~~

* Parcurgeți `prezentarea Python`_
* Folosiți tot timpul `Language Reference`_
* `Library Reference`_

Dacă tot v-a plăcut WoUSO, există un challenge_ online menit să vă
învețe Python (în stilul questurilor de la WoUSO)

.. _`prezentarea Python`: http://cdl.rosedu.org/2009/store/pdf/curs4_python.pdf
.. _`Language Reference`: http://docs.python.org/reference/index.html
.. _`Library Reference`: http://docs.python.org/library/index.html
.. _challenge: http://www.pythonchallenge.com/

Learning by doing
~~~~~~~~~~~~~~~~~

După ce ați citit câte ceva despre Python încercați să efectuați
urmatoarele task-uri:

* Functie fibo(n) care genereaza sirul lui Fibonacci pana la n.

* Se da o lista de persoane (ex: ['gigel', 'maricica', 'ionel']).
  Trebuie generat un dictionar care asociaza fiecarei persoane din lista
  o alta persoana (nu aceeasi). Ex: ['gigel':'maricica',
  'maricica':'ionel', 'ionel':'gigel'].

* Sa se extraga ultimele 10 posturi pe twitter ale unui user (ex:
  serg_ro, alexef) si sa se afiseaza la consola.

* Sa se scrie un modul cu urmatoarele specificatii::

    Clasă de bază User:
        membri: id, nume, prenume
        metode: __str__() - întoarce string sub forma "Prenume Nume (id)"
                getFullName() - întoarce string sub forma "Prenume Nume"

    Clasă Admin care extinde User:
        membri: referință la obiectul Repo
        metode: setRepo(referință la Repo) - salvează referința la Repo
    Clasă Developer care extinde User: 
        membri: referință la un obiect Project, email
        metode: __str__() - întoarce string sub forma: Prenume Nume dezvoltă proiectul NumeProiect

    Clasă Project:
        membri: nume_proiect, referință la repo, listă dezvoltatori
        metode: __str__() - întoarce numele proiectului
                addDev(instanță Developer) - adaugă Developer-ul în lista de dezvoltatori
                listDevelopers() - afișează lista de developeri (doar full name pentru fiecare)
                listContactEmails() - afișează lista de emailuri de contact (ale developer-ilor)
    Clasă Repo:
        membri: referință la obiectul Admin, listă de proiecte
        metode: listProjects() - afișează lista de proiecte din repo
                newProject(nume proiect) - întoarce o instanță de proiect, o salvează în lista de proiecte
                setAdmin(instanta Admin) - salvează referința la Admin, setează referința la Repo în Admin

* Să se calculeze suma tuturor numerelor sub 1000 care sunt multipli de
  3 sau de 5 folosind list comprehensions. Soluția trebuie să aibă o
  singură linie de cod. List Comprehension:
  http://en.wikipedia.org/wiki/List_comprehension

* Funcție care primește o cale către o imagine de pe hdd (jpg), o
  întoarce, o scalează la lățimea de 100px și o salvează png (vezi
  biblioteca PIL).

Learning Django
---------------

Download and install Django
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Download_
* Django oferă o documentație foarte bună precum și un tutorial, le
  puteți găsi aici_

.. _Download: http://www.djangoproject.com/download/
.. _aici: http://docs.djangoproject.com/en/1.2/

Learning by doing
~~~~~~~~~~~~~~~~~

Realizați o aplicație simplă care citește și afișează date despre
diverși utilizatori twitter. Veți realiza un proiect și apoi o
aplicație. Veți testa local cu runserver.

Modelul va contine informatii despre utilizator: username-ul, numele
real si descrierea si tweet-urile(care vor contine textul) printr-o
relatie many-to-one.

Aplicatia va contine 3 pagini(views):

* O pagina ce permite adăugarea utilizatorilor. Adăugarea utilizatorilor
  presupune citirea dintr-un formular a username-ului(de ex serg_ro)
  folosind twitter api și descărcarea informațiilor în baza de date
  locale. Apoi se descarcă ultimile tweet-uri. Se va face verificarea
  unicității utilizatorilor(adăugarea aceluiași utilizator nu îl va
  introduce iar în baza de date ci doar va downloada ultimile
  tweet-uri). Optional se va face și verificarea unicității
  tweet-urilor(cel mai simplu dupa text).

* O pagină ce primește prin url username-ul unui utilizator și afișează
  numele său tweet-urile pentru acesta.

* O pagina simplă ce afișează toți utilizatorii care au fost introduși
  și conține link-uri pentru view-ul de mai sus pentru fiecare
  utilizator.

Template-urile pot să fie minimale, nu e nevoie de css sau formatare
exagerată. Ca și referință implementarea mea are maxim 150 de linii de
cod cu totul.

Pentru întrebări folosiți lista de discuții wouso-dev.

Install WoUSO
-------------

Găsiți `instrucțiuni de instalare`_

.. _`instrucțiuni de instalare`: https://projects.rosedu.org/projects/wousodjango/wiki/Install
