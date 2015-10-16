from py.test import raises
from collections import namedtuple
from pytest import raises

from graphql.core.type import (
    GraphQLField,
    GraphQLNonNull,
    GraphQLInt,
    GraphQLString,
    GraphQLBoolean,
    GraphQLID,
)

from graphene.core.fields import (
    Field,
    StringField,
    NonNullField
)
from graphene.core.options import Options
from graphene.core.schema import Schema
from graphene.core.types import ObjectType


class ObjectType(object):
    _meta = Options()

    def resolve(self, *args, **kwargs):
        return None

    def can_resolve(self, *args):
        return True

    def __str__(self):
        return "ObjectType"

ot = ObjectType()

ObjectType._meta.contribute_to_class(ObjectType, '_meta')


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


def test_nonnullfield_type():
    f = NonNullField(StringField())
    f.contribute_to_class(ot, 'field_name')
    assert isinstance(f.internal_type(schema), GraphQLNonNull)


def test_stringfield_type_required():
    f = StringField(required=True)
    f.contribute_to_class(ot, 'field_name')
    assert isinstance(f.internal_field(schema), GraphQLField)
    assert isinstance(f.internal_type(schema), GraphQLNonNull)


def test_field_resolve():
    f = StringField(required=True, resolve=lambda *args: 'RESOLVED')
    f.contribute_to_class(ot, 'field_name')
    field_type = f.internal_field(schema)
    assert 'RESOLVED' == field_type.resolver(ot, 2, 3)


def test_field_resolve_type_custom():
    class MyCustomType(ObjectType):
        pass

    class OtherType(ObjectType):
        pass

    s = Schema()

    f = Field('MyCustomType')
    f.contribute_to_class(OtherType, 'field_name')
    field_type = f.get_object_type(s)
    assert field_type == MyCustomType


def test_field_resolve_type_custom():
    s = Schema()

    f = Field('self')
    f.contribute_to_class(ot, 'field_name')
    field_type = f.get_object_type(s)
    assert field_type == ot


def test_field_orders():
    f1 = Field(None)
    f2 = Field(None)
    assert f1 < f2


def test_field_orders_wrong_type():
    field = Field(None)
    try:
        assert not field < 1
    except TypeError:
        # Fix exception raising in Python3+
        pass


def test_field_eq():
    f1 = Field(None)
    f2 = Field(None)
    assert f1 != f2


def test_field_eq_wrong_type():
    field = Field(None)
    assert field != 1


def test_field_hash():
    f1 = Field(None)
    f2 = Field(None)
    assert hash(f1) != hash(f2)


def test_field_none_type_raises_error():
    s = Schema()
    f = Field(None)
    f.contribute_to_class(ot, 'field_name')
    with raises(Exception) as excinfo:
        f.internal_field(s)
    assert str(excinfo.value) == "Internal type for field ObjectType.field_name is None"


def test_field_str():
    f = StringField()
    f.contribute_to_class(ot, 'field_name')
    assert str(f) == "ObjectType.field_name"


def test_field_repr():
    f = StringField()
    assert repr(f) == "<graphene.core.fields.StringField>"


def test_field_repr_contributed():
    f = StringField()
    f.contribute_to_class(ot, 'field_name')
    assert repr(f) == "<graphene.core.fields.StringField: field_name>"
