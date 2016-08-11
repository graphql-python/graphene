import pytest

from ..field import Field
from ..objecttype import ObjectType
from ..unmountedtype import UnmountedType
from ..abstracttype import AbstractType


class MyType(object):
    pass


class Container(ObjectType):
    field1 = Field(MyType)
    field2 = Field(MyType)


class MyScalar(UnmountedType):
    def get_type(self):
        return MyType


def test_generate_objecttype():
    class MyObjectType(ObjectType):
        '''Documentation'''

    assert MyObjectType._meta.name == "MyObjectType"
    assert MyObjectType._meta.description == "Documentation"
    assert MyObjectType._meta.interfaces == tuple()
    assert MyObjectType._meta.fields == {}


def test_generate_objecttype_with_meta():
    class MyObjectType(ObjectType):

        class Meta:
            name = 'MyOtherObjectType'
            description = 'Documentation'
            interfaces = (MyType, )

    assert MyObjectType._meta.name == "MyOtherObjectType"
    assert MyObjectType._meta.description == "Documentation"
    assert MyObjectType._meta.interfaces == (MyType, )


def test_generate_objecttype_with_fields():
    class MyObjectType(ObjectType):
        field = Field(MyType)

    assert 'field' in MyObjectType._meta.fields


def test_ordered_fields_in_objecttype():
    class MyObjectType(ObjectType):
        b = Field(MyType)
        a = Field(MyType)
        field = MyScalar()
        asa = Field(MyType)

    assert list(MyObjectType._meta.fields.keys()) == ['b', 'a', 'field', 'asa']


def test_generate_objecttype_inherit_abstracttype():
    class MyAbstractType(AbstractType):
        field1 = MyScalar(MyType)

    class MyObjectType(ObjectType, MyAbstractType):
        field2 = MyScalar(MyType)

    assert MyObjectType._meta.fields.keys() == ['field1', 'field2']
    assert [type(x) for x in MyObjectType._meta.fields.values()] == [Field, Field]


def test_generate_objecttype_inherit_abstracttype_reversed():
    class MyAbstractType(AbstractType):
        field1 = MyScalar(MyType)

    class MyObjectType(MyAbstractType, ObjectType):
        field2 = MyScalar(MyType)

    assert MyObjectType._meta.fields.keys() == ['field1', 'field2']
    assert [type(x) for x in MyObjectType._meta.fields.values()] == [Field, Field]


def test_generate_objecttype_unmountedtype():
    class MyObjectType(ObjectType):
        field = MyScalar(MyType)

    assert 'field' in MyObjectType._meta.fields
    assert isinstance(MyObjectType._meta.fields['field'], Field)


def test_parent_container_get_fields():
    assert list(Container._meta.fields.keys()) == ['field1', 'field2']


def test_objecttype_as_container_only_args():
    container = Container("1", "2")
    assert container.field1 == "1"
    assert container.field2 == "2"


def test_objecttype_as_container_args_kwargs():
    container = Container("1", field2="2")
    assert container.field1 == "1"
    assert container.field2 == "2"


def test_objecttype_as_container_few_kwargs():
    container = Container(field2="2")
    assert container.field2 == "2"


def test_objecttype_as_container_all_kwargs():
    container = Container(field1="1", field2="2")
    assert container.field1 == "1"
    assert container.field2 == "2"


def test_objecttype_as_container_extra_args():
    with pytest.raises(IndexError) as excinfo:
        Container("1", "2", "3")

    assert "Number of args exceeds number of fields" == str(excinfo.value)


def test_objecttype_as_container_invalid_kwargs():
    with pytest.raises(TypeError) as excinfo:
        Container(unexisting_field="3")

    assert "'unexisting_field' is an invalid keyword argument for Container" == str(excinfo.value)
