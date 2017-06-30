Docker
======

There is a ``Dockerfile`` prepared for simpler deployment and use of repocribro. Just prepare the config file and use
`Docker`_ as you usually do:

::

    docker build -t repocribro
    docker run repocribro -d -p 5000:5000 repocribro [COMMAND]


.. _Docker: https://www.docker.com
