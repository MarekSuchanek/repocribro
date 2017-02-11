Testing
=======

This project uses the most fabulous testing tools for Python:

-  `pytest`_
-  `pytest-cov`_
-  `pytest-pep8`_
-  `betamax`_

Run tests
---------

Run tests simply by:

::

    python setup.py test

or (if you have installed dependencies):

::

    python -m pytest [options]
    pytest [options]

You can also see the tests logs at `Travis CI`_.

Betamax cassettes
-----------------

Betamax cassettes are stored in ``tests/fixtures/cassettes`` directory. If
you are not connected to theInternet, GitHub API is not working and/or
you don’t want to create own GitHub token you will use (replay) them in order
to test API client.

If you want to run your own cassettes, you need to setup system
variable ``GITHUB_TOKEN`` which will contain the GitHub personal token
(must have privileges to create/delete webhooks). You also must change variables
within ``tests/test_github.py`` specifying some of your existing repository and
also non-existing repository. Token can be created at:

* https://github.com/settings/tokens

Your test command then might look like:

::

    $ GITHUB_TOKEN=<YOUR_TOKEN> python setup.py test

or use ``export`` and ``unset``:

::

    $ export GITHUB_TOKEN=<YOUR_TOKEN>
    $ python setup.py test
    ...
    $ unset GITHUB_TOKEN

For more information, enjoy reading `Betamax documentation`_.


.. _pytest: http://doc.pytest.org/
.. _pytest-cov: https://pypi.python.org/pypi/pytest-cov
.. _pytest-pep8: https://pypi.python.org/pypi/pytest-pep8
.. _betamax: http://betamax.readthedocs.io
.. _Travis CI: https://travis-ci.org/MarekSuchanek/repocribro
.. _Betamax documentation: http://betamax.readthedocs.io/en/latest/introduction.html