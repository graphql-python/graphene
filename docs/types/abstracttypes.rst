AbstractTypes
=============

An AbstractType contains fields that can be shared among
``graphene.ObjectType``, ``graphene.Interface``,
``graphene.InputObjectType`` or other ``graphene.AbstractType``.

The basics:

- Each AbstractType is a Python class that inherits from ``graphene.AbstractType``.
- Each attribute of the AbstractType represents a field (a ``graphene.Field`` or
  ``graphene.InputField`` depending on where it is mounted)

Quick example
-------------

In this example UserFields is an ``AbstractType`` with a name. ``User`` and
``UserInput`` are two types that have their own fields
plus the ones defined in ``UserFields``.

.. code:: python

    from graphene import AbstractType, ObjectType, InputObjectType, String


    class UserFields(AbstractType):
        name = String()


    class User(ObjectType, UserFields):
        pass


    class UserInput(InputObjectType, UserFields):
        pass

.. code::

    type User {
      name: String
    }

    inputtype UserInput {
      name: String
    }
