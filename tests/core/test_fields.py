from py.test import raises
from collections import namedtuple
from pytest import raises
from graphene.core.fields import (
    Field,
    StringField,
)

from graphene.core.options import Options

from graphql.core.type import (
    GraphQLField,
    GraphQLNonNull,
    GraphQLInt,
    GraphQLString,
    GraphQLBoolean,
    GraphQLID,
)

class ObjectType(object):
    _meta = Options()
    def resolve(self, *args, **kwargs):
        return None
    def can_resolve(self, *args):
        return True

ot = ObjectType()

ObjectType._meta.contribute_to_class(ObjectType, '_meta')

def test_field_no_contributed_raises_error():
    f = Field(GraphQLString)
    with raises(Exception) as excinfo:
        f.field


def test_field_type():
    f = Field(GraphQLString)
    f.contribute_to_class(ot, 'field_name')
    assert isinstance(f.field, GraphQLField)
    assert f.type == GraphQLString


def test_stringfield_type():
    f = StringField()
    f.contribute_to_class(ot, 'field_name')
    assert f.type == GraphQLString


def test_stringfield_type_null():
    f = StringField(null=False)
    f.contribute_to_class(ot, 'field_name')
    assert isinstance(f.field, GraphQLField)
    assert isinstance(f.type, GraphQLNonNull)


def test_field_resolve():
    f = StringField(null=False)
    f.contribute_to_class(ot, 'field_name')
    field_type = f.field
    field_type.resolver(ot,2,3)
