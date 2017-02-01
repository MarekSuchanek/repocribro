repocribro
==========

|license| |travis| |coveralls| |docs| |pypi| |requires|


Repocribro is web application allowing users to register their GitHub repository so they can 
be managed, searched, browsed, tested, etc. (depends on used extensions) with the site. Main 
idea is to provide simple but powerful modular tool for building groups of GitHub repositories 
which are developed by different users and organizations.

*Cribro* means sieve in `Italian language`_ (origins in Latin word *cribrum*). This project 
provides tool for intelligent sifting repositories, information about them and its contents.


Typical use cases
-----------------

- **Community** - repositories hub of examples / projects related to the community (methodology, 
  standards, ...)
- **Courses** - gathering and evaluating homeworks


Specification
-------------

- Python-powered web application (`Flask`_ + `SQLAlchemy`_)
- Distributed as python package (will be on `PyPi`_) and via GitHub
- Ability to extend via python packages (from `PyPi`_)

  - Extend web interface, functionality and/or CLI commands

- Functionality

  - User login via GitHub account (will create an account in app paired with GitHub account)
  - Each user has own page with details and list of (public) repositories in app
  - User can allow/forbid own GitHub repository within app
  - Each registered repository has own page with details and history, details are gathered via 
    `GitHub API`_ and some are stored in DB
  - User can define if the repository page should be public, hidden (secret URL) or private 
    (logged owner and admins)
  - User has privileges (user/admin)

    - User = managing own repositories
    - Admin = managing everything
    - More roles can be created and privileges assigned to roles

  - Search repositories (by name, author, description, language, ...)
  - Administration zone

    - User management
    - Repositories management
    - Other settings including extension settings

  - Listening (`webhooks`_) for changes in repository:

    - ``push``
    - ``release``
    - ``repository``

  - REST API for search, repository detail and user detail (public content)
  - All/one repository check can be run as procedure (added to cron or runned at start of 
    the application)
- Documentation will be provided (`Sphinx`_, `readthedocs`_)
- Everything what can be will be tested (`pytest`_, `Travis CI`_, coverage)


Ideas for extensions
--------------------

- ``repocribro-file``

  - Read file info and store it in database for repository

- ``repocribro-test``

  - Run test/other script on repository contents and show evaluation on repository page
  - ``repocribro-test-docker``

    - Allow to run tests inside `Docker`_ (or other container) with restrictions so hosting 
      system cannot be harmed

- ``repocribro-badge``

  - Add functionality to generate badge for repository (like `shields.io`_)

- ``repocribro-<event>``

  - Adding some actions for more webhooks (issues, milestones, statuses, …)

- ``repocribro-gitlab``, ``repocribro-bitbucket``, ...
- ``repocribro-<org>``

  - Domain/organization-specific functionality


License
-------

This project is licensed under the MIT License - see the `LICENSE`_ file for more details.

.. _Italian language: https://en.wiktionary.org/wiki/cribro
.. _Flask: http://flask.pocoo.org
.. _SQLAlchemy: http://www.sqlalchemy.org
.. _PyPi: https://pypi.python.org/pypi
.. _GitHub API: https://developer.github.com/v3/
.. _webhooks: https://developer.github.com/webhooks/
.. _Sphinx: http://www.sphinx-doc.org/
.. _readthedocs: https://readthedocs.org
.. _pytest: http://doc.pytest.org
.. _Travis CI: https://travis-ci.org
.. _Docker: https://www.docker.com
.. _shields.io: http://shields.io
.. _LICENSE: LICENSE

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg
    :alt: License
    :target: LICENSE
.. |travis| image:: https://travis-ci.org/MarekSuchanek/repocribro.svg?branch=master
    :alt: Build Status
    :target: https://travis-ci.org/MarekSuchanek/repocribro
.. |coveralls| image:: https://coveralls.io/repos/github/MarekSuchanek/repocribro/badge.svg?branch=master
    :alt: Test Coverage
    :target: https://coveralls.io/github/MarekSuchanek/repocribro?branch=maste
.. |docs| image:: https://readthedocs.org/projects/pyt-twitterwall/badge/?version=latest
    :alt: Documentation Status
    :target: http://repocribro.readthedocs.io/en/latest/?badge=latest
.. |pypi| image:: https://badge.fury.io/py/repocribro.svg
    :alt: PyPi Version
    :target: https://badge.fury.io/py/repocribro
.. |requires| image:: https://requires.io/github/MarekSuchanek/repocribro/requirements.svg?branch=master
     :alt: Requirements Status
     :target: https://requires.io/github/MarekSuchanek/repocribro/requirements/?branch=master