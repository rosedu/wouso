.. _god:

Core - `God`
============

The God module controls world specific content and actions. It is going to be rewritten for every WoUSO edition.

It contains definitions and helpers for:

Guilds
    standard groups, i.e. Humans, Orcs
Levels
    guild specific, both names and conditions for progressing
Artifacts
    guild, level and game specific objects with name and picture

Each game should expose its modifiers IDs, letting God manage the
corresponding artifacts that triggers a modifier. A modifier ID is a
string, i.e. ``challenge-can-skip``. Each game implements the modifier's
logic, God just handles the world visible modifier - artifact.

:mod:`wouso.core.god.temple`
----------------------------
.. automodule:: wouso.core.god.temple
    :members:
