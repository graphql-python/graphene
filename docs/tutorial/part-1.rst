.. _tutorial-part-1:

Create your first schema
========================

What is a schema?
-----------------

A GraphQL schema describes your data model, and provides a GraphQL
server with an associated set of resolve methods that know how to fetch
data.

For a more in depth explaination you can refer to
`the GraphQL documentation <http://graphql.org/learn/schema/>`_.

Let's start by creating a simple schema with a ``Query`` that has only
one field: ``hello``. When we query it will return ``"Hello world"``.

Let's create a ``schema.py`` file and let's add the following content in it:


.. code:: python

    import graphene

    class Query(graphene.ObjectType):
        hello = graphene.String()

        def resolve_hello(self, info):
            return 'Hello world'

        schema = graphene.Schema(query=Query)

All GraphQL schemas are typed, so we need to specify the types in python.
We do this by creating a ``Query`` class that extends ``graphene.ObjectType``,
which is Graphene's way to specify a GraphQL type.

We are specifying a single field in our Query. This field will be called ``hello``
and will be of type ``String``.

For each field then we have to specify a resolver method. In this case we are
creating a basic method called ``resolve_hello`` that just returns ``"Hello world"``.

Using the schema
----------------

Then we can start querying our schema:

.. code:: python

    result = schema.execute('{ hello }')
    print(result.data['hello']) # "Hello world"

Later we will show you how to serve the schema under an HTTP endpoint
so that it can be used with JavaScript clients.

Let's now continue with :ref:`tutorial-part-2`.
