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

In this case, we need to use the ``types`` argument when creating the Schema:


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

For example with the ObjectType the ``last_name`` field name is converted to ``lastName``:

.. code:: python

    class Person(graphene.ObjectType):
        last_name = graphene.String()
        other_name = graphene.String(name='_other_Name')

In case you don't want to apply this transformation, provide a ``name`` argument to the field constructor.
``other_name`` converts to ``_other_Name`` (without further transformations).

Your query should look like:

.. code::

    {
        lastName
        _other_Name
    }


To disable this behavior, set the ``auto_camelcase`` to ``False`` upon schema instantiation:

.. code:: python

    my_schema = Schema(
        query=MyRootQuery,
        auto_camelcase=False,
    )

.. _SchemaTypeNamePrefix:

Type name prefix
--------------------------

You can specify a prefix for all type names in the schema by setting the ``type_name_prefix`` argument upon schema instantiation:

.. code:: python

    my_schema = Schema(
        query=MyRootQuery,
        mutation=MyRootMutation,
        subscription=MyRootSubscription
        type_name_prefix='MyPrefix',
    )

This is useful in a micro-services architecture to prepend the service name to all types and avoid conflicts for example.

The prefix will be added to the name of:

* Query / Mutation / Subscription
* Scalar
* ObjectType
* InputType
* Enum
* Interface
* Union

While fields and arguments name will be left untouched.

More specifically, the following schema:

.. code::

    type Query {
        inner: MyType
    }

    type MyType {
        field: String
        myUnion: MyUnion
        myBarType: MyBarType
        myFooType: MyFooType
    }

    union MyUnion = MyBarType | MyFooType

    type MyBarType {
        field(input: MyInputObjectType): String
        myInterface: MyInterface
    }

    input MyInputObjectType {
        field: String
    }

    interface MyInterface {
        field: String
    }

    type MyFooType {
        field: String
        myEnum: MyEnum
    }

    scalar MyScalar

    enum MyEnum {
        FOO
        BAR
    }

    type Mutation {
        createUser(name: String): CreateUser
    }

    type CreateUser {
        name: String
    }

    type Subscription {
        countToTen: Int
    }

Will be transformed to:

.. code::

    type Query {
        myPrefixInner: MyPrefixMyType
    }

    type MyPrefixMyType {
        field: String
        myUnion: MyPrefixMyUnion
        myBarType: MyPrefixMyBarType
        myFooType: MyPrefixMyFooType
    }

    union MyPrefixMyUnion = MyPrefixMyBarType | MyPrefixMyFooType

    type MyPrefixMyBarType {
        field(input: MyPrefixMyInputObjectType): String
        myInterface: MyPrefixMyInterface
    }

    input MyPrefixMyInputObjectType {
        field: String
    }

    interface MyPrefixMyInterface {
        field: String
    }

    type MyPrefixMyFooType {
        field: String
        myEnum: MyPrefixMyEnum
    }

    scalar MyPrefixMyScalar

    enum MyPrefixMyEnum {
        FOO
        BAR
    }

    type Mutation {
        myPrefixCreateUser(name: String): MyPrefixCreateUser
    }

    type MyPrefixCreateUser {
        name: String
    }

    type Subscription {
        myPrefixCountToTen: Int
    }

You can override the prefix for a specific type by setting the ``type_name_prefix`` property on the ``Meta`` class:

.. code:: python

    from graphene import ObjectType

    class MyGraphQlType(ObjectType):
        class Meta:
            type_name_prefix = ''

This is useful when defining external types in a federated schema for example.
