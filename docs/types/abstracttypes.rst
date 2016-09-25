AbstractTypes
=============

An AbstractType contains fields that could be shared among
``graphene.ObjectType``, ``graphene.Interface``,
``graphene.InputObjectType`` or other ``graphene.AbstractType``.

The basics:

- Each AbstractType is a Python class that inherits from ``graphene.AbstractType``.
- Each attribute of the AbstractType represents a field (could be a ``graphene.Field`` or 
  ``graphene.InputField`` depending on where is mounted)

Quick example
-------------

In this example UserFields is an ``AbstractType`` with a name. ``User`` and
``UserInput`` are two types that will have their own fields
plus the ones defined in ``UserFields``.

.. code:: python

    import graphene

    class UserFields(graphene.AbstractType):
        name = graphene.String()

    class User(graphene.ObjectType, UserFields):
        pass

    class UserInput(graphene.InputObjectType, UserFields):
        pass


.. code::

    type User {
      name: String
    }

    inputtype UserInput {
      name: String
    }
