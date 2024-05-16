Getting started
===============

Introduction
------------

What is GraphQL?
~~~~~~~~~~~~~~~~

GraphQL is a query language for your API.

It provides a standard way to:

* *describe data provided by a server* in a statically typed **Schema**
* *request data* in a **Query** which exactly describes your data requirements and
* *receive data* in a **Response** containing only the data you requested.

For an introduction to GraphQL and an overview of its concepts, please refer to `the official GraphQL documentation`_.

.. _the official GraphQL documentation: http://graphql.org/learn/

What is Graphene?
~~~~~~~~~~~~~~~~~

Graphene is a library that provides tools to implement a GraphQL API in Python using a *code-first* approach.

Compare Graphene's *code-first* approach to building a GraphQL API with *schema-first* approaches like `Apollo Server`_ (JavaScript) or Ariadne_ (Python). Instead of writing GraphQL **Schema Definition Language (SDL)**, we write Python code to describe the data provided by your server.

.. _Apollo Server: https://www.apollographql.com/docs/apollo-server/

.. _Ariadne: https://ariadnegraphql.org/

Graphene is fully featured with integrations for the most popular web frameworks and ORMs. Graphene produces schemas that are fully compliant with the GraphQL spec and provides tools and patterns for building a Relay-Compliant API as well.

An example in Graphene
----------------------

Let’s build a basic GraphQL schema to say "hello" and "goodbye" in Graphene.

When we send a **Query** requesting only one **Field**, ``hello``, and specify a value for the ``firstName`` **Argument**...

.. code::

    {
      hello(firstName: "friend")
    }

...we would expect the following Response containing only the data requested (the ``goodbye`` field is not resolved).

.. code::

   {
     "data": {
       "hello": "Hello friend!"
     }
   }


Requirements
~~~~~~~~~~~~

-  Python (3.8, 3.9, 3.10, 3.11, pypy)
-  Graphene (3.0)

Project setup
~~~~~~~~~~~~~

.. code:: bash

    pip install "graphene>=3.0"

Creating a basic Schema
~~~~~~~~~~~~~~~~~~~~~~~

In Graphene, we can define a simple schema using the following code:

.. code:: python

    from graphene import ObjectType, String, Schema

    class Query(ObjectType):
        # this defines a Field `hello` in our Schema with a single Argument `first_name`
        # By default, the argument name will automatically be camel-based into firstName in the generated schema
        hello = String(first_name=String(default_value="stranger"))
        goodbye = String()

        # our Resolver method takes the GraphQL context (root, info) as well as
        # Argument (first_name) for the Field and returns data for the query Response
        def resolve_hello(root, info, first_name):
            return f'Hello {first_name}!'

        def resolve_goodbye(root, info):
            return 'See ya!'

    schema = Schema(query=Query)


A GraphQL **Schema** describes each **Field** in the data model provided by the server using scalar types like *String*, *Int* and *Enum* and compound types like *List* and *Object*. For more details refer to the Graphene :ref:`TypesReference`.

Our schema can also define any number of **Arguments** for our **Fields**. This is a powerful way for a **Query** to describe the exact data requirements for each **Field**.

For each **Field** in our **Schema**, we write a **Resolver** method to fetch data requested by a client's **Query** using the current context and **Arguments**. For more details, refer to this section on :ref:`Resolvers`.

Schema Definition Language (SDL)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the `GraphQL Schema Definition Language`_, we could describe the fields defined by our example code as shown below.

.. _GraphQL Schema Definition Language: https://graphql.org/learn/schema/

.. code::

    type Query {
      hello(firstName: String = "stranger"): String
      goodbye: String
    }

Further examples in this documentation will use SDL to describe schema created by ObjectTypes and other fields.

Querying
~~~~~~~~

Then we can start querying our **Schema** by passing a GraphQL query string to ``execute``:

.. code:: python

    # we can query for our field (with the default argument)
    query_string = '{ hello }'
    result = schema.execute(query_string)
    print(result.data['hello'])
    # "Hello stranger!"

    # or passing the argument in the query
    query_with_argument = '{ hello(firstName: "GraphQL") }'
    result = schema.execute(query_with_argument)
    print(result.data['hello'])
    # "Hello GraphQL!"

Next steps
~~~~~~~~~~

Congrats! You got your first Graphene schema working!

Normally, we don't need to directly execute a query string against our schema as Graphene provides many useful Integrations with popular web frameworks like Flask and Django. Check out :ref:`Integrations` for more information on how to get started serving your GraphQL API.
