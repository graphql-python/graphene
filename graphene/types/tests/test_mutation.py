import pytest

from ..argument import Argument
from ..dynamic import Dynamic
from ..mutation import Mutation
from ..objecttype import ObjectType
from ..scalars import String
from ..schema import Schema


def test_generate_mutation_no_args():
    class MyMutation(Mutation):
        '''Documentation'''

        def mutate(self, info, **args):
            return args

    assert issubclass(MyMutation, ObjectType)
    assert MyMutation._meta.name == "MyMutation"
    assert MyMutation._meta.description == "Documentation"
    resolved = MyMutation.Field().resolver(None, None, name='Peter')
    assert resolved == {'name': 'Peter'}


def test_generate_mutation_with_meta():
    class MyMutation(Mutation):

        class Meta:
            name = 'MyOtherMutation'
            description = 'Documentation'

        def mutate(self, info, **args):
            return args

    assert MyMutation._meta.name == "MyOtherMutation"
    assert MyMutation._meta.description == "Documentation"
    resolved = MyMutation.Field().resolver(None, None, name='Peter')
    assert resolved == {'name': 'Peter'}


def test_mutation_raises_exception_if_no_mutate():
    with pytest.raises(AssertionError) as excinfo:

        class MyMutation(Mutation):
            pass

    assert "All mutations must define a mutate method in it" == str(
        excinfo.value)


def test_mutation_custom_output_type():
    class User(ObjectType):
        name = String()

    class CreateUser(Mutation):

        class Arguments:
            name = String()

        Output = User

        def mutate(self, info, name):
            return User(name=name)

    field = CreateUser.Field()
    assert field.type == User
    assert field.args == {'name': Argument(String)}
    resolved = field.resolver(None, None, name='Peter')
    assert isinstance(resolved, User)
    assert resolved.name == 'Peter'


def test_mutation_execution():
    class CreateUser(Mutation):

        class Arguments:
            name = String()
            dynamic = Dynamic(lambda: String())
            dynamic_none = Dynamic(lambda: None)

        name = String()
        dynamic = Dynamic(lambda: String())

        def mutate(self, info, name, dynamic):
            return CreateUser(name=name, dynamic=dynamic)

    class Query(ObjectType):
        a = String()

    class MyMutation(ObjectType):
        create_user = CreateUser.Field()

    schema = Schema(query=Query, mutation=MyMutation)
    result = schema.execute(''' mutation mymutation {
        createUser(name:"Peter", dynamic: "dynamic") {
            name
            dynamic
        }
    }
    ''')
    assert not result.errors
    assert result.data == {
        'createUser': {
            'name': 'Peter',
            'dynamic': 'dynamic',
        }
    }


def test_mutation_no_fields_output():
    class CreateUser(Mutation):
        name = String()

        def mutate(self, info):
            return CreateUser()

    class Query(ObjectType):
        a = String()

    class MyMutation(ObjectType):
        create_user = CreateUser.Field()

    schema = Schema(query=Query, mutation=MyMutation)
    result = schema.execute(''' mutation mymutation {
        createUser {
            name
        }
    }
    ''')
    assert not result.errors
    assert result.data == {
        'createUser': {
            'name': None,
        }
    }
