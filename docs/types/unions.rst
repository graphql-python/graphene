Unions
======

Union types are very similar to interfaces, but they don't get
to specify any common fields between the types.

The basics:

- Each Union is a Python class that inherits from ``graphene.Union``.
- Unions don't have any fields on it, just links to the possible objecttypes.

Quick example
-------------

This example model defines several ObjectTypes with their own fields.
``SearchResult`` is the implementation of ``Union`` of this object types.

.. code:: python

    from graphene import ObjectType, String, Int, Union


    class Human(ObjectType):
        name = String()
        born_in = String()


    class Droid(ObjectType):
        name = String()
        primary_function = String()


    class Starship(ObjectType):
        name = String()
        length = Int()


    class SearchResult(Union, types=(Human, Droid, Starship)):
        pass


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

