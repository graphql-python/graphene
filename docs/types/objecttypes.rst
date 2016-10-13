ObjectTypes
===========

An ObjectType is the single, definitive source of information about your
data. It contains the essential fields and behaviors of the data you’re
querying.

The basics:

- Each ObjectType is a Python class that inherits 
  ``graphene.ObjectType``.
- Each attribute of the ObjectType represents a ``Field``.

Quick example
-------------

This example model defines a Person, which has a first\_name and
last\_name:

.. code:: python

    import graphene

    class Person(graphene.ObjectType):
        first_name = graphene.String()
        last_name = graphene.String()
        full_name = graphene.String()

        def resolve_full_name(self, args, context, info):
            return '{} {}'.format(self.first_name, self.last_name)

**first\_name** and **last\_name** are fields of the ObjectType. Each
field is specified as a class attribute, and each attribute maps to a
Field.

The above ``Person`` ObjectType would have the following representation
in a schema:

.. code::

    type Person {
      firstName: String
      lastName: String
      fullName: String
    }


Resolvers
---------

A resolver is a method that resolves certain field within a
``ObjectType``. The resolver of a field will be, if not specified
otherwise, the ``resolve_{field_name}`` within the ``ObjectType``.

By default a resolver will take the ``args``, ``context`` and ``info``
arguments.

NOTE: The class resolvers in a ``ObjectType`` are treated as ``staticmethod``s
always, so the first argument in the resolver: ``self`` (or ``root``) doesn't
need to be an actual instance of the ``ObjectType``.


Quick example
~~~~~~~~~~~~~

This example model defines a ``Query`` type, which has a reverse field
that reverses the given ``word`` argument using the ``resolve_reverse``
method in the class.

.. code:: python

    import graphene

    class Query(graphene.ObjectType):
        reverse = graphene.String(word=graphene.String())

        def resolve_reverse(self, args, context, info):
            word = args.get('word')
            return word[::-1]

Resolvers outside the class
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A field could also specify a custom resolver outside the class:

.. code:: python

    import graphene

    def reverse(root, args, context, info):
        word = args.get('word')
        return word[::-1]

    class Query(graphene.ObjectType):
        reverse = graphene.String(word=graphene.String(), resolver=reverse)


Instances as data containers
----------------------------

Graphene ``ObjectType``\ s could act as containers too. So with the
previous example you could do.

.. code:: python

    peter = Person(first_name='Peter', last_name='Griffin')

    peter.first_name # prints "Peter"
    peter.last_name # prints "Griffin"

.. _Interface: /docs/interfaces/
