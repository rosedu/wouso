Interface
=========

Interface - wouso.interface module

Generic functionality
---------------------

The interface module should be aware of:

* the current theme
* game config
* God exposed config

Applications (games) should use interface specific methods of displaying
content in the base template/context, controlling sidebar, putting game
specific boxes in sidebar, header, footer, or any other zone defined by
the interface module.

Sidebar
~~~~~~~

Each game can register a sidebar box, by overriding the
`get_sidebar_widget` class method. It should use `render_string` defined in
`wouso.interface` and a template extending `sidebar_widget.html`.

Search
~~~~~~

Searching for users should be done in this module.

Static pages
------------

Static pages include: Game Story, Manual and Credits. This should be
stored externally as plain-text/markdown files and served by a interface
view.

Needs design: storage, visibility (menus?) - adding links to pages to
site_base footer.

Activity
--------

A wall page that displays actions made on the site. For example: "Bob
challenged Alice and lost".

The module should register for events send by different other modules
and log the data (in the database) that would be displayed on the wall.

:mod:`wouso.interface.activity.models`
--------------------------------------
.. automodule:: wouso.interface.activity.models
    :members:

:mod:`wouso.interface.activity.signals`
--------------------------------------
.. automodule:: wouso.interface.activity.signals
    :members:

Usage examples
~~~~~~~~

Sending events from games::

    from wouso.interface.activity import signals
    
    # games/quest/models.py
    signal_msg = u"%s has finished quest %s" % (self, self.current_quest.title)
    signals.addActivity.send(sender=None, user_from=self, user_to=self, \
                             message=signal_msg, game=QuestGame.get_instance())

    # games/qotd/views.py
    if qotd.answers[choice].correct:
        signal_msg = '%s has given a correct answer to %s'
    else:
        signal_msg = '%s has given a wrong answer to %s'
    signal_msg = signal_msg % (request.user.get_profile(), \
                               QotdGame.get_instance()._meta.verbose_name)
    signals.addActivity.send(sender=None, user_from=request.user.get_profile(), \
                             user_to=request.user.get_profile(), \
                             message=signal_msg, game=QotdGame.get_instance())

Top
---

Profile
-------

See http://swarm.cs.pub.ro/~alexef/store/profil-wouso.png


:mod:`wouso.interface`
----------------------
.. automodule:: wouso.interface
    :members:

:mod:`wouso.interface.context_processors`
-----------------------------------------
.. automodule:: wouso.interface.context_processors
    :members:

:mod:`wouso.interface.forms`
----------------------------
.. automodule:: wouso.interface.forms
    :members:

:mod:`wouso.interface.views`
----------------------------
.. automodule:: wouso.interface.views
    :members:
