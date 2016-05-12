from graphql.type import GraphQLUnionType

from graphene.core.schema import Schema
from graphene.core.types import String

from ..objecttype import ObjectType
from ..uniontype import UnionType


def test_uniontype():
    class Human(ObjectType):
        name = String()

    class Pet(ObjectType):
        name = String()

    class Thing(UnionType):
        '''Thing union description'''
        class Meta:
            types = [Human, Pet]

    schema = Schema()

    object_type = schema.T(Thing)
    assert isinstance(object_type, GraphQLUnionType)
    assert Thing._meta.type_name == 'Thing'
    assert object_type.description == 'Thing union description'
    assert object_type.get_types() == [schema.T(Human), schema.T(Pet)]
