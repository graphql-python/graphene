import pytest

from ..objecttype import ObjectType
from ..schema import Schema
from ..union import Union
from graphene.relay.connection import ConnectionField


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


def test_union_as_connection():
    class MyUnion(Union):
        class Meta:
            types = (MyObjectType1, MyObjectType2)

    class Query(ObjectType):
        objects = ConnectionField(MyUnion)

        def resolve_objects(self, args, context, info):
            return [MyObjectType1(), MyObjectType2()]

    query = '''
    query {
        objects {
            edges {
                node {
                    __typename
                }
            }
        }
    }
    '''
    schema = Schema(query=Query)
    result = schema.execute(query)
    assert not result.errors
    assert len(result.data['objects']['edges']) == 2
    assert result.data['objects']['edges'][0]['node']['__typename'] == 'MyObjectType1'
    assert result.data['objects']['edges'][1]['node']['__typename'] == 'MyObjectType2'
