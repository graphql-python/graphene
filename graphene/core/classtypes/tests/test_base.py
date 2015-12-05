from ...schema import Schema
from ...types import Field, List, NonNull, String
from ..base import ClassType, FieldsClassType


def test_classtype_basic():
    class Character(ClassType):
        '''Character description'''
    assert Character._meta.type_name == 'Character'
    assert Character._meta.description == 'Character description'


def test_classtype_advanced():
    class Character(ClassType):

        class Meta:
            type_name = 'OtherCharacter'
            description = 'OtherCharacter description'
    assert Character._meta.type_name == 'OtherCharacter'
    assert Character._meta.description == 'OtherCharacter description'


def test_classtype_definition_list():
    class Character(ClassType):
        '''Character description'''
    assert isinstance(Character.List(), List)
    assert Character.List().of_type == Character


def test_classtype_definition_nonnull():
    class Character(ClassType):
        '''Character description'''
    assert isinstance(Character.NonNull(), NonNull)
    assert Character.NonNull().of_type == Character


def test_fieldsclasstype_definition_order():
    class Character(ClassType):
        '''Character description'''

    class Query(FieldsClassType):
        name = String()
        char = Character.NonNull()

    assert list(Query._meta.fields_map.keys()) == ['name', 'char']


def test_fieldsclasstype():
    f = Field(String())

    class Character(FieldsClassType):
        field_name = f

    assert Character._meta.fields == [f]


def test_fieldsclasstype_fieldtype():
    f = Field(String())

    class Character(FieldsClassType):
        field_name = f

    schema = Schema(query=Character)
    assert Character.fields_internal_types(schema)['fieldName'] == schema.T(f)
    assert Character._meta.fields_map['field_name'] == f


def test_fieldsclasstype_inheritfields():
    name_field = Field(String())
    last_name_field = Field(String())

    class Fields1(FieldsClassType):
        name = name_field

    class Fields2(Fields1):
        last_name = last_name_field

    assert list(Fields2._meta.fields_map.keys()) == ['name', 'last_name']
