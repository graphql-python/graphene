Disable Introspection
=====================

What is the introspection ?
---------------------------

The introspection query is a query that allows you to ask the server what queries and mutations are supported. If you are a REST user, you can view it as an openapi or swagger schema.

Should I disable my introspection ?
-----------------------------------

Whether you are building a private or a public API, you might want to disable introspection :

- If you are building a public API, the introspection allows consumers (developers) to know what they can do with your API. If you disable it, it will be harder for them to use your API.
- However, if you are building a private API, the only consumers of your API will be your developers. In this case, keep the introspection open in staging environments but close it in production to reduce the attack surface.

Remember that disabling introspection does not prevent hackers from sending queries to your API. It just makes it harder to know what they can do with it.

Implementation
--------------

Graphene provides a validation rule to disable introspection. It ensures that your schema cannot be introspected.

You just need to import the ``DisableIntrospection`` class from ``graphene.validation``.

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
