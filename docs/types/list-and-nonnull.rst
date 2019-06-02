Lists and Non-Null
==================

Object types, scalars, and enums are the only kinds of types you can
define in Graphene. But when you use the types in other parts of the
schema, or in your query variable declarations, you can apply additional
type modifiers that affect validation of those values.

NonNull
-------

.. code:: python

    from graphene import ObjectType, NonNull, String


    class Character(ObjectType):
        name = NonNull(String)

Here, we're using a ``String`` type and marking it as Non-Null by wrapping
it using the ``NonNull`` class. This means that our server always expects
to return a non-null value for this field, and if it ends up getting a
null value that will actually trigger a GraphQL execution error,
letting the client know that something has gone wrong.


The previous ``NonNull`` code snippet is also equivalent to:

.. code:: python

    from graphene import ObjectType, String


    class Character(ObjectType):
        name = String(required=True)

List
----

.. code:: python

    from graphene import ObjectType, List, String


    class Character(ObjectType):
        appears_in = List(String)

Lists work in a similar way: We can use a type modifier to mark a type as a
``List``, which indicates that this field will return a list of that type.
It works the same for arguments, where the validation step will expect a list
for that value.

NonNull Lists
-------------

By default items in a list will be considered nullable. To define a list without
any nullable items the type needs to be marked as ``NonNull``. For example:

.. code:: python

    from graphene import ObjectType, List, NonNull, String


    class Character(ObjectType):
        appears_in = List(NonNull(String))

The above results in the type definition:

.. code::

    type Character {
        appearsIn: [String!]
    }
