Scalars
=======

Graphene defines the following base Scalar Types:

- ``graphene.String``
- ``graphene.Int``
- ``graphene.Float``
- ``graphene.Boolean``
- ``graphene.ID``

Graphene also provides custom scalars for Dates, Times, and JSON:

- ``graphene.types.datetime.DateTime``
- ``graphene.types.datetime.Time``
- ``graphene.types.json.JSONString``


Custom scalars
--------------

You can create a custom scalar for your schema.
The following is an example for creating a DateTime scalar:

.. code:: python

    import datetime
    from graphene.types import Scalar
    from graphql.language import ast

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

If a scalar is mounted in an ``ObjectType``, ``Interface`` or
``Mutation``, they act as ``Field``\ s:

.. code:: python

    class Person(graphene.ObjectType):
        name = graphene.String()

    # Is equivalent to:
    class Person(graphene.ObjectType):
        name = graphene.Field(graphene.String)


**Note:** when using the ``Field`` constructor directly, pass the type and
not an instance.


If the types are mounted in a ``Field``, they act as ``Argument``\ s:

.. code:: python

    graphene.Field(graphene.String, to=graphene.String())

    # Is equivalent to:
    graphene.Field(graphene.String, to=graphene.Argument(graphene.String()))
