import pytest

from ..schema import Schema
from ..objecttype import ObjectType
from ..scalars import String
from ..field import Field


class InnerType(ObjectType):
    field = String()


class Query(ObjectType):
    inner = Field(InnerType)


def test_schema():
    schema = Schema(Query)
    assert schema.get_query_type() == schema.get_graphql_type(Query)


def test_schema_get_type():
    schema = Schema(Query)
    assert schema.Query == Query
    assert schema.InnerType == InnerType


def test_schema_get_type_error():
    schema = Schema(Query)
    with pytest.raises(AttributeError) as exc_info:
        schema.X

    assert str(exc_info.value) == 'Type "X" not found in the Schema'


def test_schema_str():
    schema = Schema(Query)
    assert str(schema) == """schema {
  query: Query
}

type InnerType {
  field: String
}

type Query {
  inner: InnerType
}
"""


def test_schema_introspect():
    schema = Schema(Query)
    assert '__schema' in schema.introspect()


def test_schema_external_resolution():
    class InnerTypeResolvers(object):
        def resolve_field(self, args, context, info):
            return self['key']

    class QueryResolvers(object):
        def resolve_inner(self, args, context, info):
            return {'key': 'value'}

    schema = Schema(Query, resolvers={
        'Query': QueryResolvers,
        'InnerType': InnerTypeResolvers,
    })

    result = schema.execute('{ inner { field } }')
    assert not result.errors
    assert result.data == {
        'inner': {
            'field': 'value'
        }
    }
