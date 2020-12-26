repocribro
==========

|license| |docs| |pypi| |requires|


Repocribro is web application allowing users to register their GitHub repository so they can 
be managed, searched, browsed, tested, etc. (depends on used extensions) with the site. Main 
idea is to provide simple but powerful modular tool for building groups of GitHub repositories 
which are developed by different users and organizations.

*Cribro* means sieve in `Italian language`_ (origins in Latin word *cribrum*). This project 
provides tool for intelligent sifting repositories, information about them and its contents.

Typical use cases of Repocribro:

- **Community** - repositories hub of examples / projects related to the community (methodology, 
  standards, ...)
- **Courses** - gathering and evaluating homeworks

Installation and usage
----------------------

Installation is done via standard way by ``setup.py`` file, alternatively you can install
by ``pip`` but there are just major releases and bugfixed versions. You need to have Python
3.5+ (tested with 3.5 and 3.6), all dependencies will be installed automatically.

::

    $ python setup.py install
    $ repocribro --version
    $ repocribro --help

You can also setup virtual Python environment before installation:

::

    $ python -venv env
    $ . env/bin/activate
    (env) $ python3 setup.py install

For running the application you will need to set up the configuration with GitHub client ID and
secret, security keys, database and so on.

For details please visit `repocribro.readthedocs.io`_.

Bugs, ideas, extensions and experience
--------------------------------------

If you find any bug, get any idea or have any experience with **Repocribro** - let us know via
`issues@GitHub`_. **Repocribro** is extensible, if you are developing any extension or have an
idea for some new extension, let us know via `issues@GitHub`_ too. Please use a corresponding
label.

For details please visit `repocribro.readthedocs.io`_ and `wiki@GitHub`_.

License
-------

This project is licensed under the MIT License - see the `LICENSE`_ file for more details.

.. _Italian language: https://en.wiktionary.org/wiki/cribro
.. _repocribro.readthedocs.io: http://repocribro.readthedocs.io/en/latest/
.. _wiki@GitHub: https://github.com/MarekSuchanek/repocribro/wiki
.. _issues@GitHub: https://github.com/MarekSuchanek/repocribro/issues
.. _LICENSE: LICENSE

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg
    :alt: License
    :target: LICENSE
.. |docs| image:: https://readthedocs.org/projects/pyt-twitterwall/badge/?version=latest
    :alt: Documentation Status
    :target: http://repocribro.readthedocs.io/en/latest/?badge=latest
.. |pypi| image:: https://badge.fury.io/py/repocribro.svg
    :alt: PyPi Version
    :target: https://badge.fury.io/py/repocribro
.. |requires| image:: https://requires.io/github/MarekSuchanek/repocribro/requirements.svg?branch=develop
     :alt: Requirements Status
     :target: https://requires.io/github/MarekSuchanek/repocribro/requirements/?branch=develop
