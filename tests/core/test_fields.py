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


class Schema(object):
    pass

schema = Schema()


def test_field_no_contributed_raises_error():
    f = Field(GraphQLString)
    with raises(Exception) as excinfo:
        f.internal_field(schema)


def test_field_type():
    f = Field(GraphQLString)
    f.contribute_to_class(ot, 'field_name')
    assert isinstance(f.internal_field(schema), GraphQLField)
    assert f.internal_type(schema) == GraphQLString


def test_field_name_automatic_camelcase():
    f = Field(GraphQLString)
    f.contribute_to_class(ot, 'field_name')
    assert f.name == 'fieldName'


def test_field_name_use_name_if_exists():
    f = Field(GraphQLString, name='my_custom_name')
    f.contribute_to_class(ot, 'field_name')
    assert f.name == 'my_custom_name'


def test_stringfield_type():
    f = StringField()
    f.contribute_to_class(ot, 'field_name')
    assert f.internal_type(schema) == GraphQLString


def test_stringfield_type_null():
    f = StringField(null=False)
    f.contribute_to_class(ot, 'field_name')
    assert isinstance(f.internal_field(schema), GraphQLField)
    assert isinstance(f.internal_type(schema), GraphQLNonNull)


def test_field_resolve():
    f = StringField(null=False, resolve=lambda *args: 'RESOLVED')
    f.contribute_to_class(ot, 'field_name')
    field_type = f.internal_field(schema)
    assert 'RESOLVED' == field_type.resolver(ot, 2, 3)


def test_field_resolve_type_custom():
    class MyCustomType(object):
        pass

    class Schema(object):

        def get_type(self, name):
            if name == 'MyCustomType':
                return MyCustomType

    s = Schema()

    f = Field('MyCustomType')
    f.contribute_to_class(ot, 'field_name')
    field_type = f.get_object_type(s)
    assert field_type == MyCustomType


def test_field_resolve_type_custom():
    s = Schema()

    f = Field('self')
    f.contribute_to_class(ot, 'field_name')
    field_type = f.get_object_type(s)
    assert field_type == ot
