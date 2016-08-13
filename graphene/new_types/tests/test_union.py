import pytest

from ..objecttype import ObjectType
from ..union import Union


class MyObjectType1(ObjectType):
    pass


class MyObjectType2(ObjectType):
    pass


def test_generate_union():
    class MyUnion(Union):
        '''Documentation'''
        class Meta:
            types = (MyObjectType1, MyObjectType2)

    assert MyUnion._meta.name == "MyUnion"
    assert MyUnion._meta.description == "Documentation"
    assert MyUnion._meta.types == (MyObjectType1, MyObjectType2)


def test_generate_union_with_meta():
    class MyUnion(Union):
        class Meta:
            name = 'MyOtherUnion'
            description = 'Documentation'
            types = (MyObjectType1, MyObjectType2)

    assert MyUnion._meta.name == "MyOtherUnion"
    assert MyUnion._meta.description == "Documentation"


def test_generate_union_with_no_types():
    with pytest.raises(Exception) as exc_info:
        class MyUnion(Union):
            pass

    assert str(exc_info.value) == 'Must provide types for Union MyUnion.'
