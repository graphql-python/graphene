import pytest

from graphql import GraphQLInterfaceType, GraphQLField, GraphQLString, GraphQLInterfaceType

from ..interface import Interface
from ..field import Field


def test_generate_interface():
    class MyInterface(Interface):
        '''Documentation'''
        pass

    graphql_type = MyInterface._meta.graphql_type
    assert isinstance(graphql_type, GraphQLInterfaceType)
    assert graphql_type.name == "MyInterface"
    assert graphql_type.description == "Documentation"


def test_generate_interface_with_meta():
    class MyInterface(Interface):
        class Meta:
            name = 'MyOtherInterface'
            description = 'Documentation'

    graphql_type = MyInterface._meta.graphql_type
    assert isinstance(graphql_type, GraphQLInterfaceType)
    assert graphql_type.name == "MyOtherInterface"
    assert graphql_type.description == "Documentation"


def test_empty_interface_has_meta():
    class MyInterface(Interface):
        pass

    assert MyInterface._meta


def test_generate_interface_with_fields():
    class MyInterface(Interface):
        field = Field(GraphQLString)

    graphql_type = MyInterface._meta.graphql_type
    fields = graphql_type.get_fields()
    assert 'field' in fields


def test_interface_inheritance():
    class MyInheritedInterface(Interface):
        inherited = Field(GraphQLString)

    class MyInterface(MyInheritedInterface):
        field = Field(GraphQLString)

    graphql_type = MyInterface._meta.graphql_type
    fields = graphql_type.get_fields()
    assert 'field' in fields
    assert 'inherited' in fields
    assert fields['field'] > fields['inherited']


def test_interface_instance():
    class MyInterface(Interface):
        inherited = Field(GraphQLString)

    with pytest.raises(Exception) as excinfo:
        MyInterface()

    assert "An interface cannot be intitialized" in str(excinfo.value)


def test_interface_add_fields_in_reused_graphql_type():
    MyGraphQLType = GraphQLInterfaceType('MyGraphQLType', fields={
        'field': GraphQLField(GraphQLString)
    })

    with pytest.raises(AssertionError) as excinfo:
        class GrapheneInterface(Interface):
            field = Field(GraphQLString)

            class Meta:
                graphql_type = MyGraphQLType

    assert "cannot be mounted in" in str(excinfo.value)
