Implementing custom validators
==============================

GraphQL uses query validators to check if Query AST is valid and can be executed. Every GraphQL server implements
standard query validators. For example, there is an validator that tests if queried field exists on queried type, that
makes query fail with "Cannot query field on type" error if it doesn't.

If you need more complex validation than presented before, you can implement your own query validators. All custom query
validators should extend the `ValidationRule`_ base class importable from the ``graphql.validation.rules`` module. Query
validators are visitor classes. They are instantiated at the time of query validation with one required argument
(context: ASTValidationContext). In order to perform validation, your validator class should define one or more of
``enter_*`` and ``leave_*`` methods. For possible enter/leave items as well as details on function documentation, please
see contents of the visitor module. To make validation fail, you should call validator's report_error method with the
instance of GraphQLError describing failure reason.

Implementing your custom validators
-----------------------------------

Here is an example query validator that only allows queries fields with a name of even length.

.. code:: python

    from graphql import GraphQLError
    from graphql.language import FieldNode
    from graphql.validation import ValidationRule


    class MyCustomValidationRule(ValidationRule):
        def enter_field(self, node: FieldNode, *_args):
            if len(node.name.value) % 2 == 0:
                # Here the query length is even, so we allow it.
                return
            else:
                # Here the query length is odd, so we don't want to allow it.
                # Calling self.report_error will make the query fail with the error message.
                self.report_error(
                    GraphQLError(
                        f"Cannot query '{field_name}': length is odd.", node,
                    )
                )

.. _ValidationRule: https://github.com/graphql-python/graphql-core/blob/v3.0.5/src/graphql/validation/rules/__init__.py#L37