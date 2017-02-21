Lists and Non-Null
==================

Object types, scalars, and enums are the only kinds of types you can
define in Graphene. But when you use the types in other parts of the
schema, or in your query variable declarations, you can apply additional
type modifiers that affect validation of those values.

NonNull
-------

.. code:: python

    import graphene

    class Character(graphene.ObjectType):
        name = graphene.NonNull(graphene.String)


Here, we're using a ``String`` type and marking it as Non-Null by wrapping
it using the ``NonNull`` class. This means that our server always expects
to return a non-null value for this field, and if it ends up getting a
null value that will actually trigger a GraphQL execution error,
letting the client know that something has gone wrong.


The previous ``NonNull`` code snippet is also equivalent to:

.. code:: python

    import graphene

    class Character(graphene.ObjectType):
        name = graphene.String(required=True)


List
----

.. code:: python

    import graphene

    class Character(graphene.ObjectType):
        appears_in = graphene.List(graphene.String)

Lists work in a similar way: We can use a type modifier to mark a type as a
``List``, which indicates that this field will return a list of that type.
It works the same for arguments, where the validation step will expect a list
for that value.
