Schema
======

A Schema is created by supplying the root types of each type of operation, query and mutation (optional).
A schema definition is then supplied to the validator and executor.

.. code:: python

    my_schema = Schema(
        query=MyRootQuery,
        mutation=MyRootMutation,
    )

Types
-----

There are some cases where the schema cannot access all of the types that we plan to have.
For example, when a field returns an ``Interface``, the schema doesn't know about any of the
implementations.

In this case, we need to use the ``types`` argument when creating the Schema.


.. code:: python

    my_schema = Schema(
        query=MyRootQuery,
        types=[SomeExtraObjectType, ]
    )


Querying
--------

To query a schema, call the ``execute`` method on it.


.. code:: python

    my_schema.execute('{ lastName }')


Auto CamelCase field names
--------------------------

By default all field and argument names (that are not
explicitly set with the ``name`` arg) will be converted from
``snake_case`` to ``camelCase`` (as the API is usually being consumed by a js/mobile client)

For example with the ObjectType

.. code:: python

    class Person(graphene.ObjectType):
        last_name = graphene.String()
        other_name = graphene.String(name='_other_Name')

the ``last_name`` field name is converted to ``lastName``.

In case you don't want to apply this transformation, provide a ``name`` argument to the field constructor.
``other_name`` converts to ``_other_Name`` (without further transformations).

Your query should look like

.. code::

    {
        lastName
        _other_Name
    }


To disable this behavior, set the ``auto_camelcase`` to ``False`` upon schema instantiation.

.. code:: python

    my_schema = Schema(
        query=MyRootQuery,
        auto_camelcase=False,
    )
