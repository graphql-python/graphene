from pytest import deprecated_call

from ..abstracttype import AbstractType
from ..field import Field
from ..objecttype import ObjectType
from ..unmountedtype import UnmountedType


class MyType(ObjectType):
    pass


class MyScalar(UnmountedType):
    def get_type(self):
        return MyType


def test_abstract_objecttype_warn_deprecation():
    with deprecated_call():

        # noinspection PyUnusedLocal
        class MyAbstractType(AbstractType):
            field1 = MyScalar()


def test_generate_objecttype_inherit_abstracttype():
    with deprecated_call():

        class MyAbstractType(AbstractType):
            field1 = MyScalar()

        class MyObjectType(ObjectType, MyAbstractType):
            field2 = MyScalar()

    assert MyObjectType._meta.description is None
    assert MyObjectType._meta.interfaces == ()
    assert MyObjectType._meta.name == "MyObjectType"
    assert list(MyObjectType._meta.fields) == ["field1", "field2"]
    assert list(map(type, MyObjectType._meta.fields.values())) == [Field, Field]
