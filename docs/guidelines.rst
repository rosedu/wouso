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
