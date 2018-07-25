.. _usage-privileges:

Privileges and Roles
====================

In Repocribro, there are defined roles that can be assigned to user
accounts. Each account can have several roles and role can be assigned
to several accounts. Some pages and actions can be accessible just to
some roles.

On top of that, to allow higher granularity of permissions, each role
has a list of action privileges. Some actions can be restricted with such
privilege instead of whole role.

Roles and privileges can be simply managed in the administration web
interface of repocribro. As administrator, you can define new roles with
different privileges and assign user to them. Repocribro implements simple
wildcarding of action privileges, so ``*`` for role ``admin`` means that
the role can perform all actions defined now or in the future.


Core roles
----------

It is recommended to have three roles described in the table below - for
not-logged users, default for users and for administrators.

.. csv-table:: Core roles
    :header: "Name", "Privileges", "Description"
    :file: roles.csv

Core action privileges
----------------------

There action privileges are defined in the core and can be used.

.. csv-table:: Core action privileges
    :header: "Name", "Description"
    :file: actions.csv


