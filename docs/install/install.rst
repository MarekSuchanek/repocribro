Installation options
====================

This application can be installed via standard ``setuptools``, for
more information read `Python docs - Installing Python Module`_. Check
the :doc:`requirements` before installation.

PyPi
----

-  https://pypi.python.org/pypi/repocribro

You can use pip tool to install the package **repocribro** from `PyPi`_:

::

    $ pip install repocribro

setup.py
--------

Or download the repository from `GitHub`_ and run:

::

    $ python3 setup.py install


Check installation
------------------

After the successful installation you should be able to run:

::

    $ repocribro --version
    repocribro v0.1

.. _GitHub: https://github.com/MarekSuchanek/repocribro
.. _PyPi: https://pypi.python.org
.. _Python docs - Installing Python Module: https://docs.python.org/3.5/installing/index.html


Become an admin
---------------

After first start you should login into web app via GitHub and
then you can use ``assign-role`` command to become an ``admin``.

::

    $ repocribro assign-role --login MarekSuchanek --role admin
    Loaded extensions: core
    Role admin not in DB... adding
    Role admin added to MarekSuchanek
