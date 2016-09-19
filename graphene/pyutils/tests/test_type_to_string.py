from ...types import ObjectType, String, Int, Boolean, ID, Float, Enum, Field

from ..type_to_string import object_type_to_string


class _MyEnum(Enum):
    TEST = 'something'
    OTHER_TEST = 'else'


class _SimpleMessage(ObjectType):
    field1 = String()
    field2 = Int()
    field3 = Boolean()
    field4 = Float()
    field5 = ID()
    field6 = Field(_MyEnum)


class _Container(ObjectType):
    field1 = String()
    field2 = Field(_SimpleMessage)


def test_object_type_to_string_stringifys_empty_object_type():
    s = _SimpleMessage()
    assert object_type_to_string(s) == '_SimpleMessage()'


def test_object_type_to_string_stringifys_non_nested_object_type():
    s1 = _SimpleMessage(field1='1')
    assert object_type_to_string(s1) == (
        '_SimpleMessage(\n'
        "    field1='1'\n"
        ')'
    )

    s2 = _SimpleMessage(field1='1', field2=1, field3=True, field4=4.0, field5='ID',
                        field6=_MyEnum.TEST)
    assert object_type_to_string(s2) == (
        '_SimpleMessage(\n'
        "    field1='1',\n"
        '    field2=1,\n'
        '    field3=True,\n'
        '    field4=4.0,\n'
        "    field5='ID',\n"
        '    field6=EnumTypeMeta.TEST\n'
        ')'
    )


def test_object_type_to_string_stringifys_nested_object_type():
    s1 = _SimpleMessage(field1='1', field2=1, field3=True, field4=4.0, field5='ID',
                        field6=_MyEnum.TEST)
    c1 = _Container(field1='1', field2=s1)
    assert object_type_to_string(c1) == (
        '_Container(\n'
        "    field1='1',\n"
        '    field2=_SimpleMessage(\n'
        "        field1='1',\n"
        '        field2=1,\n'
        '        field3=True,\n'
        '        field4=4.0,\n'
        "        field5='ID',\n"
        '        field6=EnumTypeMeta.TEST\n'
        '    )\n'
        ')'
    )


def test_object_type_to_string_stringifys_nested_object_type_full_package_name():
    s1 = _SimpleMessage(field1='1', field2=1, field3=True, field4=4.0, field5='ID',
                        field6=_MyEnum.TEST)
    c1 = _Container(field1='1', field2=s1)
    assert object_type_to_string(c1, full_package_name=True) == (
        'graphene.pyutils.tests.test_type_to_string._Container(\n'
        "    field1='1',\n"
        '    field2=graphene.pyutils.tests.test_type_to_string._SimpleMessage(\n'
        "        field1='1',\n"
        '        field2=1,\n'
        '        field3=True,\n'
        '        field4=4.0,\n'
        "        field5='ID',\n"
        '        field6=EnumTypeMeta.TEST\n'
        '    )\n'
        ')'
    )
