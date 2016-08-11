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
    assert not hasattr(MyAbstractType1, 'field1')
    assert not hasattr(MyAbstractType2, 'field2')
