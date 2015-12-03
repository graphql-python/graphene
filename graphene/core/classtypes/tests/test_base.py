from ..base import ClassType, FieldsClassType
from ...types import Field, String
from ...schema import Schema


def test_classtype_basic():
    class Character(ClassType):
        '''Character description'''
        pass
    assert Character._meta.type_name == 'Character'
    assert Character._meta.description == 'Character description'


def test_classtype_advanced():
    class Character(ClassType):
        class Meta:
            type_name = 'OtherCharacter'
            description = 'OtherCharacter description'
    assert Character._meta.type_name == 'OtherCharacter'
    assert Character._meta.description == 'OtherCharacter description'


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
