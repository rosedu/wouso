.. _game:

Core - `Game`
=============

A Game object defines a wouso pluggable game, such as Qotd, Challenge
and Quest.

1. Abstract
2. Question Pool
3. Formulas
4. Main view
5. Dummy module for easy developing new modules


Guidelines
----------

* Installed games detection is done via :func:`~wouso.core.game.get_games`
  which introspects Django for models extending
  :func:`~core.game.models.Game`
* Each game should use `proxy model inheritance`_, and provide a
  `verbose_name` meta

.. _`proxy model inheritance`: http://docs.djangoproject.com/en/1.2/topics/db/models/#proxy-models

See also
--------

* the scoring specification: :ref:`scoring`


:mod:`wouso.core.game`
----------------------
.. automodule:: wouso.core.game
    :members:

:mod:`wouso.core.game.models`
-----------------------------
.. automodule:: wouso.core.game.models
    :members:
