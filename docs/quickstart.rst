Getting started
===============

Let’s build a basic GraphQL schema from scratch.

Requirements
------------

-  Python (2.7, 3.2, 3.3, 3.4, 3.5, pypy)
-  Graphene (1.0)

Project setup
-------------

.. code:: bash

    pip install graphene --upgrade

Creating a basic Schema
-----------------------

A GraphQL schema describes your data model, and provides a GraphQL
server with an associated set of resolve methods that know how to fetch
data.

We are going to create a very simple schema, with a ``Query`` with only
one field: ``hello``. And when we query it should return ``"World"``.

.. code:: python

    import graphene

    class Query(graphene.ObjectType):
        hello = graphene.String()

        def resolve_hello(self, args, context, info):
            return 'World'

    schema = graphene.Schema(query=Query)

Querying
--------

Then, we can start querying our schema:

.. code:: python

    result = schema.execute('{ hello }')
    print result.data['hello'] # "World"

Congrats! You got your first graphene schema working!
