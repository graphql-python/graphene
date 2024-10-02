Implementing custom validators
==============================

GraphQL uses query validators to check if Query AST is valid and can be executed. Every GraphQL server implements standard query validators.

For example, a validator tests if a queried field exists on queried type, making the query fail with a "Cannot query field on type" error if it does not.

If you need more complex validation than presented before, you can implement your own query validators.

Implementing your custom validators
-----------------------------------

All custom query validators should extend the `ValidationRule`_ base class importable from the ``graphql.validation.rules`` module.
Query validators are `Visitor`_ classes.

Your custom validator should implement some methods of

In order to perform validation, your validator class should define some one or more of ``enter_*`` or ``leave_*`` methods.

Foreach methods, you will receive a node object to test:

- You can now choose to raise an error by calling ``report_error`` method with an instance of GraphQLError describing the failure reason.
- Or you can continue the parsing by returning ``None``.

Example
-------

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
.. _Visitor: https://github.com/graphql-python/graphql-core/blob/d90bf9902ca1639365639d5632861d1e18d672a9/src/graphql/language/visitor.py#L111
