Writing extensions
==================

.. toctree::
   :maxdepth: 2

   hooks

You can write your own **repocribro** extension. It's very simple,
all you need is extend the ``Extension`` class from ``repocribro.extending``,
make function returning instance of this class and direct entrypoint
in the group ``[repocribro.ext]`` on that function. Extending is done
via implementing actions on :doc:`hooks` which can return something.

While writing new plugin use please the same model, so even your extension
is also easily extensible. Big part of core repocribro is extension itself
see the module ``repocribro.ext_core``.


my_ext.py
---------

.. code-block:: python
   :linenos:

    from repocribro.extending import Extension


    class MyNewExtension(Extension):
       ...


    def make_my_new_extension():
       ...
       return MyNewExtension()


setup.py
--------

.. code-block:: python
   :linenos:

    from setuptools import setup

    ...
    setup(
        ...
        entry_points={
            'repocribro.ext': [
                'repocribro-my_ext = my_ext:make_my_new_extension'
            ]
        },
        ...
    )
    ...

