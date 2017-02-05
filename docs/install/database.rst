Database
========

In order to create and maintain the database, you can use migrations
by `Flask-Migrate`_:

::

    $ repocribro db --help


Or you can use standard `SQLAlchemy procedure`_ ``db.create_all()`` via:

::

    $ repocribro create-db


Both will try to create tables into database specified in the
:doc:`config`.

.. _Flask-Migrate: https://flask-migrate.readthedocs.io/en/latest/
.. _SQLAlchemy procedure: http://docs.sqlalchemy.org/en/latest/core/metadata.html?highlight=create_all#sqlalchemy.schema.MetaData.create_all
