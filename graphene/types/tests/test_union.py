from pytest import raises

from ..field import Field
from ..objecttype import ObjectType
from ..union import Union
from ..unmountedtype import UnmountedType


class MyObjectType1(ObjectType):
    pass


class MyObjectType2(ObjectType):
    pass


def test_generate_union():
    class MyUnion(Union):
        """Documentation"""

        class Meta:
            types = (MyObjectType1, MyObjectType2)

    assert MyUnion._meta.name == "MyUnion"
    assert MyUnion._meta.description == "Documentation"
    assert MyUnion._meta.types == (MyObjectType1, MyObjectType2)


def test_generate_union_with_meta():
    class MyUnion(Union):
        class Meta:
            name = "MyOtherUnion"
            description = "Documentation"
            types = (MyObjectType1, MyObjectType2)

    assert MyUnion._meta.name == "MyOtherUnion"
    assert MyUnion._meta.description == "Documentation"


def test_generate_union_with_no_types():
    with raises(Exception) as exc_info:

        class MyUnion(Union):
            pass

    assert str(exc_info.value) == "Must provide types for Union MyUnion."


def test_union_can_be_mounted():
    class MyUnion(Union):
        class Meta:
            types = (MyObjectType1, MyObjectType2)

    my_union_instance = MyUnion()
    assert isinstance(my_union_instance, UnmountedType)
    my_union_field = my_union_instance.mount_as(Field)
    assert isinstance(my_union_field, Field)
    assert my_union_field.type == MyUnion


def test_generate_union_with_string_references():
    class MyUnion(Union):
        class Meta:
            types = (
                "graphene.types.tests.test_union.MyObjectType1",
                "graphene.types.tests.test_union.MyObjectType2",
            )

    assert MyUnion._meta.types == (MyObjectType1, MyObjectType2)


def test_generate_union_with_lambda_references():
    class MyUnion(Union):
        class Meta:
            types = (
                lambda: MyObjectType1,
                lambda: MyObjectType2,
            )

    assert MyUnion._meta.types == (MyObjectType1, MyObjectType2)


def test_generate_union_with_mixed_references():
    class MyUnion(Union):
        class Meta:
            types = (
                MyObjectType1,
                lambda: MyObjectType2,
                "graphene.types.tests.test_union.MyObjectType1",
            )

    assert MyUnion._meta.types == (MyObjectType1, MyObjectType2, MyObjectType1)


def test_union_types_property_is_iterable():
    class MyUnion(Union):
        class Meta:
            types = (
                lambda: MyObjectType1,
                "graphene.types.tests.test_union.MyObjectType2",
            )

    first_access = MyUnion._meta.types
    second_access = MyUnion._meta.types
    assert first_access == second_access
