ObjectTypes
===========

An ObjectType is the single, definitive source of information about your
data. It contains the essential fields and behaviors of the data you’re
querying.

The basics:

- Each ObjectType is a Python class that inherits from
  ``graphene.ObjectType``.
- Each attribute of the ObjectType represents a ``Field``.

Quick example
-------------

This example model defines a Person, with a first and a last name:

.. code:: python

    import graphene

    class Person(graphene.ObjectType):
        first_name = graphene.String()
        last_name = graphene.String()
        full_name = graphene.String()

        def resolve_full_name(self):
            return '{} {}'.format(self.first_name, self.last_name)

**first\_name** and **last\_name** are fields of the ObjectType. Each
field is specified as a class attribute, and each attribute maps to a
Field.

The above ``Person`` ObjectType has the following schema representation:

.. code::

    type Person {
      firstName: String
      lastName: String
      fullName: String
    }


Resolvers
---------

A resolver is a method that resolves certain fields within a
``ObjectType``. If not specififed otherwise, the resolver of a
field is the ``resolve_{field_name}`` method on the ``ObjectType``.

By default resolvers take the arguments ``args``, ``context`` and ``info``.

NOTE: The resolvers on a ``ObjectType`` are always treated as ``staticmethod``\ s,
so the first argument to the resolver method ``self`` (or ``root``) need
not be an actual instance of the ``ObjectType``.


Quick example
~~~~~~~~~~~~~

This example model defines a ``Query`` type, which has a reverse field
that reverses the given ``word`` argument using the ``resolve_reverse``
method in the class.

.. code:: python

    import graphene

    class Query(graphene.ObjectType):
        reverse = graphene.String(word=graphene.String())

        def resolve_reverse(self, word):
            return word[::-1]

Resolvers outside the class
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A field can use a custom resolver from outside the class:

.. code:: python

    import graphene

    def reverse(root, word):
        return word[::-1]

    class Query(graphene.ObjectType):
        reverse = graphene.String(word=graphene.String(), resolver=reverse)


Instances as data containers
----------------------------

Graphene ``ObjectType``\ s can act as containers too. So with the
previous example you could do:

.. code:: python

    peter = Person(first_name='Peter', last_name='Griffin')

    peter.first_name # prints "Peter"
    peter.last_name # prints "Griffin"

.. _Interface: /docs/interfaces/
