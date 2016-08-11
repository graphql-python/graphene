import pytest

from ..field import Field
from ..abstracttype import AbstractType
from ..unmountedtype import UnmountedType


class MyType(object):
    pass


class MyScalar(UnmountedType):
    def get_type(self):
        return MyType


def test_generate_abstracttype_with_fields():
    class MyAbstractType(AbstractType):
        field = Field(MyType)

    assert 'field' in MyAbstractType._meta.fields
    assert isinstance(MyAbstractType._meta.fields['field'], Field)


def test_generate_abstracttype_with_unmountedfields():
    class MyAbstractType(AbstractType):
        field = UnmountedType(MyType)

    assert 'field' in MyAbstractType._meta.fields
    assert isinstance(MyAbstractType._meta.fields['field'], UnmountedType)


def test_generate_abstracttype_inheritance():
    class MyAbstractType1(AbstractType):
        field1 = UnmountedType(MyType)

    class MyAbstractType2(MyAbstractType1):
        field2 = UnmountedType(MyType)

    assert MyAbstractType2._meta.fields.keys() == ['field1', 'field2']


# def test_ordered_fields_in_objecttype():
#     class MyObjectType(ObjectType):
#         b = Field(MyType)
#         a = Field(MyType)
#         field = MyScalar()
#         asa = Field(MyType)

#     assert list(MyObjectType._meta.fields.keys()) == ['b', 'a', 'field', 'asa']


# def test_generate_objecttype_unmountedtype():
#     class MyObjectType(ObjectType):
#         field = MyScalar(MyType)

#     assert 'field' in MyObjectType._meta.fields
#     assert isinstance(MyObjectType._meta.fields['field'], Field)


# def test_parent_container_get_fields():
#     assert list(Container._meta.fields.keys()) == ['field1', 'field2']


# def test_objecttype_as_container_only_args():
#     container = Container("1", "2")
#     assert container.field1 == "1"
#     assert container.field2 == "2"


# def test_objecttype_as_container_args_kwargs():
#     container = Container("1", field2="2")
#     assert container.field1 == "1"
#     assert container.field2 == "2"


# def test_objecttype_as_container_few_kwargs():
#     container = Container(field2="2")
#     assert container.field2 == "2"


# def test_objecttype_as_container_all_kwargs():
#     container = Container(field1="1", field2="2")
#     assert container.field1 == "1"
#     assert container.field2 == "2"


# def test_objecttype_as_container_extra_args():
#     with pytest.raises(IndexError) as excinfo:
#         Container("1", "2", "3")

#     assert "Number of args exceeds number of fields" == str(excinfo.value)


# def test_objecttype_as_container_invalid_kwargs():
#     with pytest.raises(TypeError) as excinfo:
#         Container(unexisting_field="3")

#     assert "'unexisting_field' is an invalid keyword argument for Container" == str(excinfo.value)
