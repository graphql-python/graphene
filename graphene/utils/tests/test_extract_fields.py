from collections import OrderedDict
from graphql import GraphQLField, GraphQLString, GraphQLInterfaceType, GraphQLInt, GraphQLFloat
from ..extract_fields import extract_fields, get_base_fields

from ...types import Field, String, Argument, ObjectType


def test_extract_fields_attrs():
    attrs = {
        'field_string': Field(String),
        'string': String(),
        'other': None,
        'argument': Argument(String),
        'graphql_field': GraphQLField(GraphQLString)
    }
    extracted_fields = list(extract_fields(ObjectType, attrs))
    assert [f.name for f in extracted_fields] == ['fieldString', 'string']
    assert sorted(attrs.keys()) == ['argument', 'graphql_field', 'other']


def test_extract_fields():
    int_base = GraphQLInterfaceType('IntInterface', fields=OrderedDict([
        ('int', GraphQLField(GraphQLInt)),
        ('num', GraphQLField(GraphQLInt)),
        ('extra', GraphQLField(GraphQLInt))
    ]))
    float_base = GraphQLInterfaceType('IntInterface', fields=OrderedDict([
        ('float', GraphQLField(GraphQLFloat)),
        ('num', GraphQLField(GraphQLFloat)),
        ('extra', GraphQLField(GraphQLFloat))
    ]))

    bases = (int_base, float_base)
    base_fields = list(get_base_fields(ObjectType, bases))
    assert [f.name for f in base_fields] == ['int', 'num', 'extra', 'float']
    assert [f.type for f in base_fields] == [
        GraphQLInt,
        GraphQLInt,
        GraphQLInt,
        GraphQLFloat,
    ]
