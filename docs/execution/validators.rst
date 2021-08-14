Validators
==========

Validation rules help validate a given GraphQL query, before executing it. To help with common use
cases, graphene provides a few validation rules out of the box.


Depth limit Validator
-----------------
The depth limit validator helps to prevent execution of malicious
queries. It takes in the following arguments.

- ``max_depth`` is the maximum allowed depth for any operation in a GraphQL document.
- ``ignore`` Stops recursive depth checking based on a field name. Either a string or regexp to match the name, or a function that returns a boolean
- ``callback`` Called each time validation runs. Receives an Object which is a map of the depths for each operation.

Example
-------

Here is how you would implement depth-limiting on your schema.

.. code:: python
    from graphql import validate
    from graphene import ObjectType, Schema, String
    from graphene.validation import depth_limit_validator


    class MyQuery(ObjectType):
        name = String(required=True)


    schema = Schema(query=MyQuery)

    # Queries which have a depth more than 20
    # will not be executed.

    validation_errors = validate(
        schema=schema,
        document='THE QUERY',
        rules=(
            depth_limit_validator(
                max_depth=20
            ),
        )
    )
