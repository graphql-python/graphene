Unions
======

Union types are very similar to interfaces, but they don't get
to specify any common fields between the types.

The basics:

- Each Union is a Python class that inherits from ``graphene.Union``.
- Unions don't have any fields on it, just links to the possible objecttypes.

Quick example
-------------

This example model defines a ``Character`` interface with a name. ``Human``
and ``Droid`` are two implementations of that interface.

.. code:: python

    import graphene

    class Human(graphene.ObjectType):
        name = graphene.String()
        born_in = graphene.String()

    class Droid(graphene.ObjectType):
        name = graphene.String()
        primary_function = graphene.String()

    class Starship(graphene.ObjectType):
        name = graphene.String()
        length = graphene.Int()

    class SearchResult(graphene.Union):
        class Meta:
            types = (Human, Droid, Starship)


Wherever we return a SearchResult type in our schema, we might get a Human, a Droid, or a Starship.
Note that members of a union type need to be concrete object types;
you can't create a union type out of interfaces or other unions.

The above types have the following representation in a schema:

.. code::

    type Droid {
      name: String
      primaryFunction: String
    }

    type Human {
      name: String
      bornIn: String
    }

    type Ship {
      name: String
      length: Int
    }

    union SearchResult = Human | Droid | Starship

