import pytest

from ..mutation import Mutation
from ..objecttype import ObjectType
from ..schema import Schema
from ..scalars import String


def test_generate_mutation_no_args():
    class MyMutation(Mutation):
        '''Documentation'''
        @classmethod
        def mutate(cls, *args, **kwargs):
            pass

    assert issubclass(MyMutation, ObjectType)
    assert MyMutation._meta.name == "MyMutation"
    assert MyMutation._meta.description == "Documentation"
    assert MyMutation.Field().resolver == MyMutation.mutate


def test_generate_mutation_with_meta():
    class MyMutation(Mutation):

        class Meta:
            name = 'MyOtherMutation'
            description = 'Documentation'

        @classmethod
        def mutate(cls, *args, **kwargs):
            pass

    assert MyMutation._meta.name == "MyOtherMutation"
    assert MyMutation._meta.description == "Documentation"
    assert MyMutation.Field().resolver == MyMutation.mutate


def test_mutation_raises_exception_if_no_mutate():
    with pytest.raises(AssertionError) as excinfo:
        class MyMutation(Mutation):
            pass

    assert "All mutations must define a mutate method in it" == str(excinfo.value)


def test_mutation_execution():
    def with_metadata(gql_type, data):
        setattr(gql_type, 'metadata', data)
        return gql_type

    class CreateUser(Mutation):
        class Input:
            name = String()
            metadata = with_metadata(String(), 'service_key')

        _Input = Input

        name = String()
        external = String()

        @classmethod
        def mutate(cls, root, args, context, info):
            name = args.get('name')
            external_data = {
                'service_key': 'new_data'
            }

            metadata_type = dict(vars(cls._Input))['metadata']
            data = external_data[getattr(metadata_type, 'metadata')]
            return CreateUser(name=name, external=data)

    class Query(ObjectType):
        a = String()

    class MyMutation(ObjectType):
        create_user = CreateUser.Field()

    schema = Schema(query=Query, mutation=MyMutation)
    result = schema.execute(''' mutation mymutation {
        createUser(name:"Peter") {
            name
            external
        }
    }
    ''')
    assert not result.errors
    assert result.data == {
        'createUser': {
            'name': 'Peter',
            'external': 'new_data',
        }
    }
