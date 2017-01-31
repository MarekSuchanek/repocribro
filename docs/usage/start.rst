Usage basics
============

First you need to have prepared config file(s) with at least minimal mandatory
configuration and **repocribro** successfully installed(see :doc:`../install/index`
and :doc:`../install/config`).

::

   $ repocribro --config <config_file> [command] [command options]
   $ repocribro -c <config_file> [command] [command options]
   $ repocribro -c <config_file_1> -c <config_file_2> [command] [command options]

For all commands you can specify configuration file(s) of **repocribro** app, order
of arguments matters only if you are overriding same configuration variable in those
files. If no config files are specified those from default path will be used.

Commands
--------
After supplying configuration files you can use various commands. Full list of commands
with details are described within :doc:`commands`.

For starting the web application (server) use:

::

   $ repocribro runserver



Common options
--------------

You can also use standard ``-?``, ``--help`` and ``--version``:

::

  $ repocribro --help
  usage: repocribro [-c CFG_FILES] [-v] [-?] {runserver,db,shell,repocheck} ...

  positional arguments:
    {runserver,db,shell,repocheck}
      runserver           Runs the Flask development server i.e. app.run()
      db                  Perform database migrations
      shell               Runs a Python shell inside Flask application context.
      repocheck           Perform check procedure of repository events

  optional arguments:
    -c CFG_FILES, --config CFG_FILES
    -v, --version         show program's version number and exit
    -?, --help            show this help message and exit

  $ repocribro --version
  repocribro v0.0