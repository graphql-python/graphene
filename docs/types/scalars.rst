Scalars
=======

Graphene defines the following base Scalar Types:

- ``graphene.String``
- ``graphene.Int``
- ``graphene.Float``
- ``graphene.Boolean``
- ``graphene.ID``

Graphene also provides custom scalars for Dates and JSON:

- ``graphene.types.datetime.DateTime``
- ``graphene.types.json.JSONString``


Custom scalars
--------------

You can create custom scalars for your schema.
The following is an example for creating a DateTime scalar:

.. code:: python

    import datetime
    from graphene.core.classtypes import Scalar
    from graphql.core.language import ast

    class DateTime(Scalar):
        '''DateTime Scalar Description'''

        @staticmethod
        def serialize(dt):
            return dt.isoformat()

        @staticmethod
        def parse_literal(node):
            if isinstance(node, ast.StringValue):
                return datetime.datetime.strptime(
                    node.value, "%Y-%m-%dT%H:%M:%S.%f")

        @staticmethod
        def parse_value(value):
            return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")

Mounting Scalars
----------------

Scalars mounted in a ``ObjectType``, ``Interface`` or ``Mutation`` act as
``Field``\ s.

.. code:: python

    class Person(graphene.ObjectType):
        name = graphene.String()

    # Is equivalent to:
    class Person(graphene.ObjectType):
        name = graphene.Field(graphene.String())


Types mounted in a ``Field`` act as ``Argument``\ s.

.. code:: python

    graphene.Field(graphene.String(), to=graphene.String())

    # Is equivalent to:
    graphene.Field(graphene.String(), to=graphene.Argument(graphene.String()))
