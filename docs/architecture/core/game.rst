Game
====

A Game object defines a wouso pluggable game, such as Qotd, Challenge
and Quest.

Guidelines
----------

* Installed games detection is done via wosuo.core.game.get_games()
  which introspects Django for models extending core.game.models.Game
* Each game should use proxy model inheritance, and provide a
  verbose_name meta

Model
-----

* Game

  - fields
  - name - the same as the class name, i.e. QotdGame
  - methods
  - get_formulas() - return a list of formulas used by the game for scoring
  - get_coins() - return a list of coins used by the game

See also
--------

.. TODO link to `scoring`

* the scoring specification


:mod:`wouso.core.game`
----------------------
.. automodule:: wouso.core.game
    :members:

:mod:`wouso.core.game.models`
-----------------------------
.. automodule:: wouso.core.game.models
    :members:
