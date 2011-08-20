.. _scoring:

Core - `Scoring`
================

The Scoring module (SM) centralizes users' grading system, providing
coin type management, storage for the formulas, a few helper functions
to be used in formulas, and detailed history of gained coins.

The coins used in WoUSO are of two types: core and game specific.

An application (a game) define its grading formulas; the SM will
register and store these formulas, making them editable by an
administrator; when an action finishes, the game asks SM for a formula
calculation, with given parameters, and then pushes scores for each user
playing the game.

Coins
-----

Core
~~~~

These types of coin are available globally in the game. `God` defines
their names. Each game can modify the amount of these coins for each
user.

Their id are kept simple and suggestive.

Right now, only `points` core type coin is defined.

Game specific
~~~~~~~~~~~~~

Each game can define specific types of coin he offers to the user.
`God` can override their names. Only the game defining the coin type
can modify the amount for a user.

Their id is prefixed with the owner game, i.e. `challenge-stamina`.

Examples
~~~~~~~~

Given the core coins::

    Id: points
    Name: Galbeni


\1. Qotd registers one simple formula, giving 3 points for a correct
answer::

    Name: qotd-ok
    Formula: points=3


After an user plays Qotd, it asks SM to calculate the points, with no
parameters; then save them for the user::

    # self - a Qotd game instance
    # 'qotd-ok' - the formula id
    core.scoring.score(user1, self, 'qotd-ok')


\2. Challenge adds a coin type::

    Id: challenge-stamina
    Name: Fight Stamina

and registers two formulas, one for won challenge, another for lost::

    Name: challenge-lost
    Formula: points=-3, challenge-stamina=-100

    Name: challenge-won
    Formula: points=3 + ({level1} - {level2}) * 0.5, challenge-stamina=50


After playing a challenge::

    core.scoring.score(user1, self, 'challenge-lost' external_id=challenge.id)
    core.scoring.score(user2, self, 'challenge-won', external_id=challenge.id, level1=user1.level, level2=user2.level)


Discussion
----------

* AE: maybe we need a generic method: ``score(user, game, points)``
  for simpler use cases?
* AE: also, there shall be an api for getting user's scores history
* GVS: Answering to AE and maybe an improvement, too long to keep it
  here, i made a new page.
  (https://projects.rosedu.org/projects/wousodjango/wiki/CoreModulesScoringDiscutionTemp)
* AE: added GVS coins; not adding helper methods right now, because the
  current proposal defines only game specific - ``get_users_at_level_x`` -
  which should be implemented by God - who knows levels
* AE: added `external_id` for history


:mod:`wouso.core.scoring.models`
--------------------------------
.. automodule:: wouso.core.scoring.models
    :members:

:mod:`wouso.core.scoring.sm`
----------------------------
.. automodule:: wouso.core.scoring.sm
    :members:
