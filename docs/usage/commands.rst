CLI commands
============

There are various command for the app management some are
provided by Flask extensions, some by repocribro. You can
use option ``--help`` to get more information.

You can use both ``repocribro`` and ``flask`` commands. The
configuration must by specified by environenment variable as
described in :ref:`config`.

assign_role
-----------

Main purpose for this command is to set the initial admin
of the app without touching DB directly. Others can be then
set within administration zone of web interface.

::

    $ repocribro assign_role --login MarekSuchanek --role admin
    Loaded extensions: core
    Role admin not in DB... adding
    Role admin added to MarekSuchanek

    $ repocribro assign-role --login MarekSuchanek --role admin
    Loaded extensions: core
    User MarekSuchanek already has role admin


For more information:
::

    $ repocribro assign_role --help


check_config
------------

Commands for checking configuration currently used by repocribro.
There are two styles for printing, same syntax as is in the cfg file
(default) or just triples section key value.

::

    $ repocribro check_config
    [flask]
    secret_key = MySecretKey
    ...

    $ repocribro check_config --style triple
    flask secret_key MySecretKey
    ...


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

This command provides simple checking of one or all
repositories if there are some uncaught events within specified
time. Main idea is to get the missed events (from webhooks) due
to app outage.

::

    $ repocribro repocheck --help

runserver
---------

Runs the web application (``app.run()``), but also some settings
can be overriden like hostname, port, debugging, ...

For more information:

::

    $ repocribro run --help



shell
-----

Runs the Python shell inside the Flask app context. That can be
useful for some debugging by hand.

For more information:

::

    $ repocribro shell --help




.. _Flask-Migrate extension: https://flask-migrate.readthedocs.io
