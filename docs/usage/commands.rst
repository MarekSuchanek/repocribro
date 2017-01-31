CLI commands
============

There are various command for the app management some are
provided by Flask extensions, some by repocribro. You can
use option ``--help`` to get more information.

db (database)
-------------

Command supplied by `Flask-Migrate extension`_ provides tool
to work with database migrations (init, migrate, downgrade,
upgrade, etc.).

For more information:

::

    $ repocribro db --help

repocheck
---------

*Not implemented yet!*

This command will provide simple checking of one or all
repositories if there are some uncaught events within specified
time. Main idea is to get the missed events (from webhooks) due
to app outage.


runserver
---------

Runs the web application (``app.run()``), but also some settings
can be overriden like hostname, port, debugging, ...

For more information:

::

    $ repocribro runserver --help



shell
-----

Runs the Python shell inside the Flask app context. That can be
useful for some debugging by hand.

For more information:

::

    $ repocribro shell --help




.. _Flask-Migrate extension: https://flask-migrate.readthedocs.io