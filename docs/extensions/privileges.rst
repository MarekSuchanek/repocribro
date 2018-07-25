Privileges and Roles
====================

Again, good example is ``repocribro.ext_core``. Within your
extension you can define new roles and action privileges by methods
``provide_roles`` and ``provide_actions``. It uses `flask-principal`_
wrapped in ``flask.security.permissions`` object. After registration
of roles and action privileges, you can simply import the object and
use it to decorate controller function like this:

.. code-block:: python
   :linenos:

   import flask
   from ..security import permissions

   showcase = flask.Blueprint('showcase', __name__, url_prefix='/showcase')

   @showcase.route('test1')
   @permissions.roles.my_new_role.require(403)
   def test1():
       ...

   @showcase.route('test2')
   @permissions.actions.test_it.require(403)
   def test2():
       ...


For basics about privileges, see :ref:`usage-privileges`.


.. _flask-principal: https://pythonhosted.org/Flask-Principal/
