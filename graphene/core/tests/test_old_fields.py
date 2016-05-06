from graphql.type import (GraphQLBoolean, GraphQLField, GraphQLFloat,
                               GraphQLID, GraphQLInt, GraphQLNonNull,
                               GraphQLString)
from py.test import raises

from graphene.core.fields import (BooleanField, Field, FloatField, IDField,
                                  IntField, NonNullField, StringField)
from graphene.core.schema import Schema
from graphene.core.types import ObjectType


class MyOt(ObjectType):

    def resolve_customdoc(self, *args, **kwargs):
        '''Resolver documentation'''
        return None

    def __str__(self):
        return "ObjectType"

schema = Schema()


def test_field_no_contributed_raises_error():
    f = Field(GraphQLString)
    with raises(Exception):
        schema.T(f)


def test_field_type():
    f = Field(GraphQLString)
    f.contribute_to_class(MyOt, 'field_name')
    assert isinstance(schema.T(f), GraphQLField)
    assert schema.T(f).type == GraphQLString


def test_field_name():
    f = Field(GraphQLString)
    f.contribute_to_class(MyOt, 'field_name')
    assert f.name is None
    assert f.attname == 'field_name'


def test_field_name_use_name_if_exists():
    f = Field(GraphQLString, name='my_custom_name')
    f.contribute_to_class(MyOt, 'field_name')
    assert f.name == 'my_custom_name'


def test_stringfield_type():
    f = StringField()
    f.contribute_to_class(MyOt, 'field_name')
    assert schema.T(f) == GraphQLString


def test_idfield_type():
    f = IDField()
    f.contribute_to_class(MyOt, 'field_name')
    assert schema.T(f) == GraphQLID


def test_booleanfield_type():
    f = BooleanField()
    f.contribute_to_class(MyOt, 'field_name')
    assert schema.T(f) == GraphQLBoolean


def test_intfield_type():
    f = IntField()
    f.contribute_to_class(MyOt, 'field_name')
    assert schema.T(f) == GraphQLInt


def test_floatfield_type():
    f = FloatField()
    f.contribute_to_class(MyOt, 'field_name')
    assert schema.T(f) == GraphQLFloat


def test_nonnullfield_type():
    f = NonNullField(StringField())
    f.contribute_to_class(MyOt, 'field_name')
    assert isinstance(schema.T(f), GraphQLNonNull)


def test_stringfield_type_required():
    f = StringField(required=True).as_field()
    f.contribute_to_class(MyOt, 'field_name')
    assert isinstance(schema.T(f), GraphQLField)
    assert isinstance(schema.T(f).type, GraphQLNonNull)


def test_field_resolve():
    f = StringField(required=True, resolve=lambda *args: 'RESOLVED').as_field()
    f.contribute_to_class(MyOt, 'field_name')
    field_type = schema.T(f)
    assert 'RESOLVED' == field_type.resolver(MyOt, None, None)


def test_field_resolve_type_custom():
    class MyCustomType(ObjectType):
        pass

    f = Field('MyCustomType')

    class OtherType(ObjectType):
        field_name = f

    s = Schema()
    s.query = OtherType
    s.register(MyCustomType)

    assert s.T(f).type == s.T(MyCustomType)


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
    f.contribute_to_class(MyOt, 'field_name')
    with raises(Exception) as excinfo:
        s.T(f)
    assert str(
        excinfo.value) == "Internal type for field MyOt.field_name is None"


def test_field_str():
    f = StringField().as_field()
    f.contribute_to_class(MyOt, 'field_name')
    assert str(f) == "MyOt.field_name"


def test_field_repr():
    f = StringField().as_field()
    assert repr(f) == "<graphene.core.types.field.Field>"


def test_field_repr_contributed():
    f = StringField().as_field()
    f.contribute_to_class(MyOt, 'field_name')
    assert repr(f) == "<graphene.core.types.field.Field: field_name>"


def test_field_resolve_objecttype_cos():
    f = StringField().as_field()
    f.contribute_to_class(MyOt, 'customdoc')
    field = schema.T(f)
    assert field.description == 'Resolver documentation'
