from collections import OrderedDict

from graphql import (GraphQLField, GraphQLFloat, GraphQLInt,
                     GraphQLInterfaceType, GraphQLString)

from ...types import Argument, Field, ObjectType, String
from ..get_fields import get_fields_from_attrs, get_fields_from_types


def test_get_fields_from_attrs():
    attrs = OrderedDict((
        ('field_string', Field(String)),
        ('string', String()),
        ('other', None),
        ('argument', Argument(String)),
        ('graphql_field', GraphQLField(GraphQLString)),
    ))
    extracted_fields = OrderedDict(get_fields_from_attrs(ObjectType, attrs))
    assert [f for f in extracted_fields.keys()] == ['field_string', 'string']


def test_get_fields_from_types():
    int_base = GraphQLInterfaceType('IntInterface', fields=OrderedDict([
        ('int', GraphQLField(GraphQLInt)),
        ('num', GraphQLField(GraphQLInt)),
        ('extra', GraphQLField(GraphQLInt))
    ]))
    float_base = GraphQLInterfaceType('FloatInterface', fields=OrderedDict([
        ('float', GraphQLField(GraphQLFloat)),
        ('num', GraphQLField(GraphQLFloat)),
        ('extra', GraphQLField(GraphQLFloat))
    ]))

    bases = (int_base, float_base)
    base_fields = OrderedDict(get_fields_from_types(bases))
    assert [f for f in base_fields.keys()] == ['int', 'num', 'extra', 'float']
    assert [f.type for f in base_fields.values()] == [
        GraphQLInt,
        GraphQLInt,
        GraphQLInt,
        GraphQLFloat,
    ]
