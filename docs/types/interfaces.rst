Interfaces
==========

An Interface contains the essential fields that will be implemented among
multiple ObjectTypes.

The basics:
- Each Interface is a Python class that inherits from ``graphene.Interface``.
- Each attribute of the Interface represents a GraphQL field.

Quick example
-------------

This example model defines a Character, which has a name. ``Human`` and
``Droid`` are two of the Interface implementations.

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


**name** is a field in the ``Character`` interface that will be in both
``Human`` and ``Droid`` ObjectTypes (as those implement the ``Character``
interface). Each ObjectType also define extra fields at the same
time.

The above types would have the following representation in a schema:

.. code:: graphql

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
