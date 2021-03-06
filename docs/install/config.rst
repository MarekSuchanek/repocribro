.. _config:

Configuration
=============

You can see example configuration files at:

* ``config/app.example.cfg``
* ``config/auth.example.cfg``
* ``config/db.example.cfg``

  **!!!**  If you are going to publish your configuration somewhere
  make sure, that it does not contain any secret information
  like passwords or API tokens!

Syntax of configuration files is `standard INI`_, parsed by `ConfigParser`_.
Names of variables are case insensitive. Configuration can be in separate
configuration files but if there are same variables within same sections
there will overriding depending on the order of files.

Default config file can be also specified with environment variable:

::

    $ export REPOCRIBRO_CONFIG_FILE='/path/to/config.cfg'
    $ python
    Python 3.5.2 (default, Oct 14 2016, 12:54:53)
    [GCC 6.2.1 20160916 (Red Hat 6.2.1-2)] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from repocribro.app import app
    >>> app.run()

You can also take advantage of `python-dotenv`_ and specify configuration
in `.env` file.

.. _python-dotenv: https://github.com/theskumar/python-dotenv

Application
-----------

You can specify any of the Flask (or extensions) configuration variables
that is supposed to be placed to ``app.config``. Just use same name (it
can be also lowercase). These configurations must be done in ``[flask]``
section. Mandatory attribute is ``SECRET_KEY`` used for the `session signing`_,
this key is of course **private**.

* http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values

For example:

.. code-block:: ini

    [flask]
    # something is wrong, I want to debug
    DEBUG = true
    # random secret key (use os.urandom())
    SECRET_KEY = VeryPseudoRandomSuchSecret

Webroot in subdirectory
^^^^^^^^^^^^^^^^^^^^^^^

If you are running the application in subdirectiory and not whole (sub)domain
(e.g. myportal.xyz/repocribro/), then you probably want to use the setting
``APPLICATION_ROOT`` which will in case of repocribro not only set appropriately
session path but also make URLs correct and working.

.. code-block:: ini
    :caption: Repocribro config (part)

    [flask]
    APPLICATION_ROOT = /repocribro
    # ... other config

.. code-block:: nginx
    :caption: NGINX config (part)

    location ~ /repocribro(/.*)$ {
        proxy_pass http://127.0.0.1:5000/repocribro$1;
		proxy_set_header Host $host;
    }


Database
--------

Next you need to specify configuration of your database. Flask extension
Flask-SQLAlchemy is used so again configuration needs to be done within
section ``[flask]``.

* http://flask-sqlalchemy.pocoo.org/2.1/config/#configuration-keys

    **!!!**  If file contains DB password and username keep it **private**!

For example:

.. code-block:: ini

    [flask]
    # SQLite is enough, just testing
    SQLALCHEMY_DATABASE_URI = sqlite:////tmp/test.db

GitHub
------

For communication with GitHub OAuth you are going to need **Client ID** and
**Client secret**. Also for working with webhooks secret key must be set-up
so every incoming message can be verified. Specify those in ``[github]``
section of config.

* https://developer.github.com/v3/oauth/
* https://github.com/settings/applications/new
* https://developer.github.com/webhooks/securing/

    **!!!**  Always keep file with this configuration **private**!

For example:

.. code-block:: ini

    [github]
    # Client ID & secret is obtained by creating OAuth app
    CLIENT_ID = myAppClientIdFromGitHub
    CLIENT_SECRET = myAppClientSecretFromGitHub
    # Webhook secret for signing should be randomly generated
    WEBHOOKS_SECRET = someRandomSecretKeyForWebhooks


.. _standard INI: https://en.wikipedia.org/wiki/INI_file
.. _ConfigParser: https://docs.python.org/3/library/configparser.html
.. _session signing: http://flask.pocoo.org/docs/0.12/quickstart/#sessions


Core customization
------------------

You can specify name and logo for your deployment of repocribro within
``repocribro-core`` section. More options will be added later.


For example:

.. code-block:: ini

    [repocribro-core]
    # custom name
    NAME = myRepocribro
    # custom logo URL
    LOGO = https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Logo_TV_2015.svg/2000px-Logo_TV_2015.svg.png
    # landing page text
    LANDING_TEXT = <p>Landing text paragraph number 1</p>
                   <p>Landing text paragraph number 2</p>
    # landing page picture (defaults to LOGO)
    LANDING_PICTURE = https://assets-cdn.github.com/images/modules/logos_page/Octocat.png
    # navbar classes (dark/light, defaults to dark)
    NAVBAR_STYLE = light