Interfaces
==========

An Interface contains the essential fields that will be implemented by
multiple ObjectTypes.

The basics:

- Each Interface is a Python class that inherits from ``graphene.Interface``.
- Each attribute of the Interface represents a GraphQL field.

Quick example
-------------

This example model defines a ``Character`` interface with a name. ``Human``
and ``Droid`` are two implementations of that interface.

.. code:: python

    import graphene

    class Character(graphene.Interface):
        name = graphene.String()

    # Human is a Character implementation
    class Human(ObjectType):
        class Meta:
            interfaces = (Character, )

        born_in = graphene.String()

    # Droid is a Character implementation
    class Droid(Character):
        class Meta:
            interfaces = (Character, )

        function = graphene.String()


``name`` is a field on the ``Character`` interface that will also exist on both
the ``Human`` and ``Droid`` ObjectTypes (as those implement the ``Character``
interface). Each ObjectType may define additional fields.

The above types have the following representation in a schema:

.. code::

    interface Character {
      name: String
    }

    type Droid implements Character {
      name: String
      function: String
    }

    type Human implements Character {
      name: String
      bornIn: String
    }
