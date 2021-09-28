Query Validation
==========
GraphQL uses query validators to check if Query AST is valid and can be executed. Every GraphQL server implements
standard query validators. For example, there is an validator that tests if queried field exists on queried type, that
makes query fail with "Cannot query field on type" error if it doesn't.

To help with common use cases, graphene provides a few validation rules out of the box.


Depth limit Validator
-----------------
The depth limit validator helps to prevent execution of malicious
queries. It takes in the following arguments.

- ``max_depth`` is the maximum allowed depth for any operation in a GraphQL document.
- ``ignore`` Stops recursive depth checking based on a field name. Either a string or regexp to match the name, or a function that returns a boolean
- ``callback`` Called each time validation runs. Receives an Object which is a map of the depths for each operation.

Usage
-------

Here is how you would implement depth-limiting on your schema.

.. code:: python

    from graphql import validate, parse
    from graphene import ObjectType, Schema, String
    from graphene.validation import depth_limit_validator


    class MyQuery(ObjectType):
        name = String(required=True)


    schema = Schema(query=MyQuery)

    # queries which have a depth more than 20
    # will not be executed.

    validation_errors = validate(
        schema=schema,
        document_ast=parse('THE QUERY'),
        rules=(
            depth_limit_validator(
                max_depth=20
            ),
        )
    )


Disable Introspection
---------------------
the disable introspection validation rule ensures that your schema cannot be introspected.
This is a useful security measure in production environments.

Usage
-------

Here is how you would disable introspection for your schema.

.. code:: python

    from graphql import validate, parse
    from graphene import ObjectType, Schema, String
    from graphene.validation import DisableIntrospection


    class MyQuery(ObjectType):
        name = String(required=True)


    schema = Schema(query=MyQuery)

    # introspection queries will not be executed.

    validation_errors = validate(
        schema=schema,
        document_ast=parse('THE QUERY'),
        rules=(
            DisableIntrospection,
        )
    )


Implementing custom validators
------------------------------
All custom query validators should extend the `ValidationRule <https://github.com/graphql-python/graphql-core/blob/v3.0.5/src/graphql/validation/rules/__init__.py#L37>`_
base class importable from the graphql.validation.rules module. Query validators are visitor classes. They are
instantiated at the time of query validation with one required argument (context: ASTValidationContext). In order to
perform validation, your validator class should define one or more of enter_* and leave_* methods. For possible
enter/leave items as well as details on function documentation, please see contents of the visitor module. To make
validation fail, you should call validator's report_error method with the instance of GraphQLError describing failure
reason. Here is an example query validator that visits field definitions in GraphQL query and fails query validation
if any of those fields are blacklisted:

.. code:: python

    from graphql import GraphQLError
    from graphql.language import FieldNode
    from graphql.validation import ValidationRule


    my_blacklist = (
        "disallowed_field",
    )


    def is_blacklisted_field(field_name: str):
        return field_name.lower() in my_blacklist


    class BlackListRule(ValidationRule):
        def enter_field(self, node: FieldNode, *_args):
            field_name = node.name.value
            if not is_blacklisted_field(field_name):
                return

            self.report_error(
                GraphQLError(
                    f"Cannot query '{field_name}': field is blacklisted.", node,
                )
            )

