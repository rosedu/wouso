Guidelines
==========

Coding style
------------

* set ts=4
* import order::

    import python-modules
    import django-modules
    import wouso.[core|interface]
    import game-modules

Function usage
--------------

in your views, use wouso.interface.render_response instead of render_to_response or HttpResponse

Logging
-------

log everything
see Logging

Testing
-------

write unit tests, see Scoring or Qotd for examples.

Documentation
-------------

WoUSO documentation is maintained using Sphinx_ in the repository, under
``/docs``. To update it:

* Edit a page::

    cd docs
    vim guidelines.rst

* Build locally::

    make html

* Check the generated HTML. It's under ``_build/html``.

* Upload to publc server::

    scp -r _build/html wouso@rosedu.org:public_html/docs

.. _Sphinx: http://sphinx.pocoo.org/
