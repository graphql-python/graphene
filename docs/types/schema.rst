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

There are some cases where the schema could not access all the types that we plan to have.
For example, when a field returns an ``Interface``, the schema doesn't know any of the
implementations.

In this case, we would need to use the ``types`` argument when creating the Schema.


.. code:: python

    my_schema = Schema(
        query=MyRootQuery,
        types=[SomeExtraObjectType, ]
    )


Querying
--------

If you need to query a schema, you can directly call the ``execute`` method on it.


.. code:: python
    
    my_schema.execute('{ lastName }')


Auto CamelCase field names
--------------------------

By default all field and argument names (that are not 
explicitly set with the ``name`` arg) will be converted from
`snake_case` to `camelCase` (`as the API is usually being consumed by a js/mobile client`)

So, for example if we have the following ObjectType

.. code:: python

    class Person(graphene.ObjectType):
        last_name = graphene.String()
        other_name = graphene.String(name='_other_Name')

Then the ``last_name`` field name is converted to ``lastName``.

In the case we don't want to apply any transformation, we can specify
the field name with the ``name`` argument. So ``other_name`` field name
would be converted to ``_other_Name`` (without any other transformation).

So, you would need to query with:

.. code::

    {
        lastName
        _other_Name
    }


If you want to disable this behavior, you set use the ``auto_camelcase`` argument
to ``False`` when you create the Schema.

.. code:: python

    my_schema = Schema(
        query=MyRootQuery,
        auto_camelcase=False,
    )
