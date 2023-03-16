Disable Introspection
=====================

What is the introspection ?
---------------------------

The introspection query is a query that allows you to ask the server what queries and mutations are supported. If you
comes from REST, you can view it as a openapi or swagger schema.

Disabling it or not ?
---------------------

Depending if you are building a private or a public API, you might want to disable introspection or not. If you are
building a public API, the introspection allows consumers (developers) to know what they can do with your API. If you
disable it, it will be harder for them to use your API. But if you are building a private API, the only consumers of
your API will be your own developers. In this case, you might want to keep the introspection open in staging
environments but close it in production to reduce the attack surface.

Keep in mind that disabling introspection does not prevent hackers to send queries to your API. It just makes it harder
to know what they can do with it.

Implementation
--------------

Graphene provides a validation rule to disable introspection. It ensures that your schema cannot be introspected. You
just need to import the ``DisableIntrospection`` class from ``graphene.validation``.


Here is a code example of how you can disable introspection for your schema.

.. code:: python

    from graphql import validate, parse
    from graphene import ObjectType, Schema, String
    from graphene.validation import DisableIntrospection


    class MyQuery(ObjectType):
        name = String(required=True)


    schema = Schema(query=MyQuery)

    # introspection queries will not be executed.

    validation_errors = validate(
        schema=schema.graphql_schema,
        document_ast=parse('THE QUERY'),
        rules=(
            DisableIntrospection,
        )
    )
