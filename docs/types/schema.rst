Schema
======

A GraphQL **Schema** defines the types and relationships between **Fields** in your API.

A Schema is created by supplying the root :ref:`ObjectType` of each operation, query (mandatory), mutation and subscription.

Schema will collect all type definitions related to the root operations and then supply them to the validator and executor.

.. code:: python

    my_schema = Schema(
        query=MyRootQuery,
        mutation=MyRootMutation,
        subscription=MyRootSubscription
    )

A Root Query is just a special :ref:`ObjectType` that defines the fields that are the entrypoint for your API. Root Mutation and Root Subscription are similar to Root Query, but for different operation types:

* Query fetches data
* Mutation changes data and retrieves the changes
* Subscription sends changes to clients in real-time

Review the `GraphQL documentation on Schema`_ for a brief overview of fields, schema and operations.

.. _GraphQL documentation on Schema: https://graphql.org/learn/schema/


Querying
--------

To query a schema, call the ``execute`` method on it. See :ref:`SchemaExecute` for more details.


.. code:: python

    query_string = 'query whoIsMyBestFriend { myBestFriend { lastName } }'
    my_schema.execute(query_string)

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

.. _SchemaAutoCamelCase:

Auto camelCase field names
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
