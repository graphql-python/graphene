
from graphql.type import (GraphQLArgument, GraphQLEnumType, GraphQLEnumValue,
                          GraphQLField, GraphQLObjectType, GraphQLString,
                          GraphQLInterfaceType, GraphQLInputObjectField,
                          GraphQLInputObjectType)

from ..dynamic import Dynamic
from ..enum import Enum
from ..field import Field
from ..inputfield import InputField
from ..objecttype import ObjectType
from ..inputobjecttype import InputObjectType
from ..interface import Interface
from ..scalars import String
from ..typemap import TypeMap


def test_enum():
    class MyEnum(Enum):
        '''Description'''
        foo = 1
        bar = 2

        @property
        def description(self):
            return 'Description {}={}'.format(self.name, self.value)

        @property
        def deprecation_reason(self):
            if self == MyEnum.foo:
                return 'Is deprecated'

    typemap = TypeMap([MyEnum])
    assert 'MyEnum' in typemap
    graphql_enum = typemap['MyEnum']
    assert isinstance(graphql_enum, GraphQLEnumType)
    assert graphql_enum.name == 'MyEnum'
    assert graphql_enum.description == 'Description'
    values = graphql_enum.values
    assert values == [
        GraphQLEnumValue(name='foo', value=1, description='Description foo=1', deprecation_reason='Is deprecated'),
        GraphQLEnumValue(name='bar', value=2, description='Description bar=2'),
    ]


def test_objecttype():
    class MyObjectType(ObjectType):
        '''Description'''
        foo = String(bar=String(description='Argument description', default_value='x'), description='Field description')
        bar = String(name='gizmo')

        def resolve_foo(self, args, info):
            return args.get('bar')

    typemap = TypeMap([MyObjectType])
    assert 'MyObjectType' in typemap
    graphql_type = typemap['MyObjectType']
    assert isinstance(graphql_type, GraphQLObjectType)
    assert graphql_type.name == 'MyObjectType'
    assert graphql_type.description == 'Description'

    fields = graphql_type.fields
    assert list(fields.keys()) == ['foo', 'gizmo']
    foo_field = fields['foo']
    assert isinstance(foo_field, GraphQLField)
    assert foo_field.description == 'Field description'
    f = MyObjectType.resolve_foo
    assert foo_field.resolver == getattr(f, '__func__', f)
    assert foo_field.args == {
        'bar': GraphQLArgument(GraphQLString, description='Argument description', default_value='x')
    }


def test_dynamic_objecttype():
    class MyObjectType(ObjectType):
        '''Description'''
        bar = Dynamic(lambda: Field(String))
        own = Field(lambda: MyObjectType)

    typemap = TypeMap([MyObjectType])
    assert 'MyObjectType' in typemap
    assert list(MyObjectType._meta.fields.keys()) == ['bar', 'own']
    graphql_type = typemap['MyObjectType']

    fields = graphql_type.fields
    assert list(fields.keys()) == ['bar', 'own']
    assert fields['bar'].type == GraphQLString
    assert fields['own'].type == graphql_type


def test_interface():
    class MyInterface(Interface):
        '''Description'''
        foo = String(bar=String(description='Argument description', default_value='x'), description='Field description')
        bar = String(name='gizmo', first_arg=String(), other_arg=String(name='oth_arg'))
        own = Field(lambda: MyInterface)

        def resolve_foo(self, args, info):
            return args.get('bar')

    typemap = TypeMap([MyInterface])
    assert 'MyInterface' in typemap
    graphql_type = typemap['MyInterface']
    assert isinstance(graphql_type, GraphQLInterfaceType)
    assert graphql_type.name == 'MyInterface'
    assert graphql_type.description == 'Description'

    fields = graphql_type.fields
    assert list(fields.keys()) == ['foo', 'gizmo', 'own']
    assert fields['own'].type == graphql_type
    assert (fields['gizmo'].args.keys()) == ['firstArg', 'oth_arg']
    foo_field = fields['foo']
    assert isinstance(foo_field, GraphQLField)
    assert foo_field.description == 'Field description'
    assert not foo_field.resolver # Resolver not attached in interfaces
    assert foo_field.args == {
        'bar': GraphQLArgument(GraphQLString, description='Argument description', default_value='x')
    }


def test_inputobject():
    class MyInputObjectType(InputObjectType):
        '''Description'''
        foo = String(description='Field description')
        bar = String(name='gizmo')
        own = InputField(lambda: MyInputObjectType)

        def resolve_foo(self, args, info):
            return args.get('bar')

    typemap = TypeMap([MyInputObjectType])
    assert 'MyInputObjectType' in typemap
    graphql_type = typemap['MyInputObjectType']
    assert isinstance(graphql_type, GraphQLInputObjectType)
    assert graphql_type.name == 'MyInputObjectType'
    assert graphql_type.description == 'Description'

    fields = graphql_type.fields
    assert list(fields.keys()) == ['foo', 'gizmo', 'own']
    assert fields['own'].type == graphql_type
    foo_field = fields['foo']
    assert isinstance(foo_field, GraphQLInputObjectField)
    assert foo_field.description == 'Field description'
