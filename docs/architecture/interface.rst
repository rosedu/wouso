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

Top
---

Profile
-------

See http://swarm.cs.pub.ro/~alexef/store/profil-wouso.png


