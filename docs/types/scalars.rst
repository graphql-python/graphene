.. _Scalars:

Scalars
=======

All Scalar types accept the following arguments. All are optional:

``name``: *string*

    Override the name of the Field.

``description``: *string*

    A description of the type to show in the GraphiQL browser.

``required``: *boolean*

    If ``True``, the server will enforce a value for this field. See `NonNull <../list-and-nonnull.html#nonnull>`_. Default is ``False``.

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
    values. Int is a signed 32‐bit integer per the
    `GraphQL spec <https://facebook.github.io/graphql/June2018/#sec-Int>`_

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

Graphene also provides custom scalars for common types:

``graphene.Date``

    Represents a Date value as specified by `iso8601 <https://en.wikipedia.org/wiki/ISO_8601>`_.

.. code:: python

    import datetime
    from graphene import Schema, ObjectType, Date

    class Query(ObjectType):
        one_week_from = Date(required=True, date_input=Date(required=True))

        def resolve_one_week_from(root, info, date_input):
            assert date_input == datetime.date(2006, 1, 2)
            return date_input + datetime.timedelta(weeks=1)

    schema = Schema(query=Query)

    results = schema.execute("""
        query {
            oneWeekFrom(dateInput: "2006-01-02")
        }
    """)

    assert results.data == {"oneWeekFrom": "2006-01-09"}


``graphene.DateTime``

    Represents a DateTime value as specified by `iso8601 <https://en.wikipedia.org/wiki/ISO_8601>`_.

.. code:: python

    import datetime
    from graphene import Schema, ObjectType, DateTime

    class Query(ObjectType):
        one_hour_from = DateTime(required=True, datetime_input=DateTime(required=True))

        def resolve_one_hour_from(root, info, datetime_input):
            assert datetime_input == datetime.datetime(2006, 1, 2, 15, 4, 5)
            return datetime_input + datetime.timedelta(hours=1)

    schema = Schema(query=Query)

    results = schema.execute("""
        query {
            oneHourFrom(datetimeInput: "2006-01-02T15:04:05")
        }
    """)

    assert results.data == {"oneHourFrom": "2006-01-02T16:04:05"}

``graphene.Time``

    Represents a Time value as specified by `iso8601 <https://en.wikipedia.org/wiki/ISO_8601>`_.

.. code:: python

    import datetime
    from graphene import Schema, ObjectType, Time

    class Query(ObjectType):
        one_hour_from = Time(required=True, time_input=Time(required=True))

        def resolve_one_hour_from(root, info, time_input):
            assert time_input == datetime.time(15, 4, 5)
            tmp_time_input = datetime.datetime.combine(datetime.date(1, 1, 1), time_input)
            return (tmp_time_input + datetime.timedelta(hours=1)).time()

    schema = Schema(query=Query)

    results = schema.execute("""
        query {
            oneHourFrom(timeInput: "15:04:05")
        }
    """)

    assert results.data == {"oneHourFrom": "16:04:05"}

``graphene.JSONString``

    Represents a JSON string.

.. code:: python

    from graphene import Schema, ObjectType, JSONString, String

    class Query(ObjectType):
        update_json_key = JSONString(
            required=True,
            json_input=JSONString(required=True),
            key=String(required=True),
            value=String(required=True)
        )

        def resolve_update_json_key(root, info, json_input, key, value):
            assert json_input == {"name": "Jane"}
            json_input[key] = value
            return json_input

    schema = Schema(query=Query)

    results = schema.execute("""
        query {
            updateJsonKey(jsonInput: "{\\"name\\": \\"Jane\\"}", key: "name", value: "Beth")
        }
    """)

    assert results.data == {"updateJsonKey": "{\"name\": \"Beth\"}"}


``graphene.Base64``

    Represents a Base64 encoded string.

.. code:: python

    from graphene import Schema, ObjectType, Base64

    class Query(ObjectType):
        increment_encoded_id = Base64(
            required=True,
            base64_input=Base64(required=True),
        )

        def resolve_increment_encoded_id(root, info, base64_input):
            assert base64_input == "4"
            return int(base64_input) + 1

    schema = Schema(query=Query)

    results = schema.execute("""
        query {
            incrementEncodedId(base64Input: "NA==")
        }
    """)

    assert results.data == {"incrementEncodedId": "NQ=="}


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
