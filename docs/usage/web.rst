Web application
===============

Public usage
------------

Anonymous (unauthenticated) used can browse public content
of the web application which includes:

* landing with basic info
* search
* user/organization profiles
* public repositories with their releases and updates

Authentication
--------------

User can authenticate via GitHub OAuth with scope:

* ``repo`` = read and manage user repositories (with private)
* ``user`` = read user information (with private)
* ``admin:webhook`` = add/remove webhooks


User management
---------------

Every activate (not banned) user can manage which of
his/her repositories should be listed within application as:

* public = everyone can see them
* hidden = only people with secret URL can see them
* private = only owner or administrator can see them

Information about user account can be synchronized as well as
the repository information. When activating the repository webhook
is added. Because webhook can be deleted at GitHub by hand, user
can recreate the webhook again (he can't do it by hand because
doesn't know the webhooks secret).

Administration
--------------

Managing user accounts, roles and repositories (not owned) can
be done in administration zone. Same principles as in user management
zone.

REST API
--------

There is also REST API (only GET) for all GitHub entities, but it
will be reworked soon (because the repo privacy & compatibility issues).

The actual is done by `Flask-Restless`_ with collections:

* ``user``
* ``org``
* ``repo``
* ``push``
* ``commit``
* ``release``

.. _Flask-Restless: https://flask-restless.readthedocs.io/en/stable/
