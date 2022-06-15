from pytest import raises

from ..field import Field
from ..objecttype import ObjectType
from ..union import Union
from ..unmountedtype import UnmountedType
from ..schema import Schema
from ..scalars import String


class MyObjectType1(ObjectType):
    name = Field(String)


class MyObjectType2(ObjectType):
    not_name = Field(String)


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


def test_resolve_type_custom():
    class MyUnion(Union):
        class Meta:
            types = (MyObjectType1, MyObjectType2)

        @classmethod
        def resolve_type(cls, instance, info):
            if 'name' in instance:
                return MyObjectType1
            else:
                return MyObjectType2

    class Query(ObjectType):
        test = Field(MyUnion)

        def resolve_test(_, info):
            return {'name': 'Type 1'}

    schema = Schema(query=Query)
    result = schema.execute(
        """
        query {
            test {
                __typename
                ...on MyObjectType1 {
                    name
                }
            }
        }
        """
    )
    assert not result.errors
    assert result.data == {"test": {"__typename": "MyObjectType1", "name": "Type 1"}}
