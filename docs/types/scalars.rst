Scalars
=======

All Scalar types accept the following arguments. All are optional:

``name``: *string*

    Override the name of the Field.

``description``: *string*

    A description of the type to show in the GraphiQL browser.

``required``: *boolean*

    If ``True``, the server will enforce a value for this field. See `NonNull <./list-and-nonnull.html#nonnull>`_. Default is ``False``.

``deprecation_reason``: *string*

    Provide a deprecation reason for the Field.

``default_value``: *any*

    Provide a default value for the Field.



Base scalars
------------

Graphene defines the following base Scalar Types:

``graphene.String``

    Represents textual data, represented as UTF-8
    character sequences. The String type is most often used by GraphQL to
    represent free-form human-readable text.

``graphene.Int``

    Represents non-fractional signed whole numeric
    values. Int can represent values between `-(2^53 - 1)` and `2^53 - 1` since
    represented in JSON as double-precision floating point numbers specified
    by `IEEE 754 <http://en.wikipedia.org/wiki/IEEE_floating_point>`_.

``graphene.Float``

    Represents signed double-precision fractional
    values as specified by
    `IEEE 754 <http://en.wikipedia.org/wiki/IEEE_floating_point>`_.

``graphene.Boolean``

    Represents `true` or `false`.

``graphene.ID``

    Represents a unique identifier, often used to
    refetch an object or as key for a cache. The ID type appears in a JSON
    response as a String; however, it is not intended to be human-readable.
    When expected as an input type, any string (such as `"4"`) or integer
    (such as `4`) input value will be accepted as an ID.

Graphene also provides custom scalars for Dates, Times, and JSON:

``graphene.types.datetime.Date``

    Represents a Date value as specified by `iso8601 <https://en.wikipedia.org/wiki/ISO_8601>`_.

``graphene.types.datetime.DateTime``

    Represents a DateTime value as specified by `iso8601 <https://en.wikipedia.org/wiki/ISO_8601>`_.

``graphene.types.datetime.Time``

    Represents a Time value as specified by `iso8601 <https://en.wikipedia.org/wiki/ISO_8601>`_.

``graphene.types.json.JSONString``

    Represents a JSON string.


Custom scalars
--------------

You can create custom scalars for your schema.
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

Scalars mounted in a ``ObjectType``, ``Interface`` or ``Mutation`` act as
``Field``\ s.

.. code:: python

    class Person(graphene.ObjectType):
        name = graphene.String()

    # Is equivalent to:
    class Person(graphene.ObjectType):
        name = graphene.Field(graphene.String)


**Note:** when using the ``Field`` constructor directly, pass the type and
not an instance.

Types mounted in a ``Field`` act as ``Argument``\ s.


.. code:: python

    graphene.Field(graphene.String, to=graphene.String())

    # Is equivalent to:
    graphene.Field(graphene.String, to=graphene.Argument(graphene.String))
