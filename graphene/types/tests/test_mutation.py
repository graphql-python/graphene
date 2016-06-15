import pytest

from graphql import GraphQLObjectType, GraphQLString

from ..field import Field
from ..mutation import Mutation
from ..objecttype import ObjectType
from ..scalars import String


def test_generate_mutation_no_args():
    class MyMutation(Mutation):
        '''Documentation'''
        @classmethod
        def mutate(cls, *args, **kwargs):
            pass

    assert issubclass(MyMutation, ObjectType)
    graphql_type = MyMutation._meta.graphql_type
    assert isinstance(graphql_type, GraphQLObjectType)
    assert graphql_type.name == "MyMutation"
    assert graphql_type.description == "Documentation"


def test_generate_mutation_with_args():
    class MyMutation(Mutation):
        '''Documentation'''
        class Input:
            s = String()

        @classmethod
        def mutate(cls, *args, **kwargs):
            pass

    graphql_type = MyMutation._meta.graphql_type
    field = MyMutation.Field()
    assert isinstance(graphql_type, GraphQLObjectType)
    assert graphql_type.name == "MyMutation"
    assert graphql_type.description == "Documentation"
    assert isinstance(field, Field)
    assert field.type == MyMutation._meta.graphql_type
    assert 's' in field.args
    assert field.args['s'].type == GraphQLString


def test_generate_mutation_with_meta():
    class MyMutation(Mutation):

        class Meta:
            name = 'MyOtherMutation'
            description = 'Documentation'

        @classmethod
        def mutate(cls, *args, **kwargs):
            pass

    graphql_type = MyMutation._meta.graphql_type
    assert isinstance(graphql_type, GraphQLObjectType)
    assert graphql_type.name == "MyOtherMutation"
    assert graphql_type.description == "Documentation"


def test_empty_mutation_has_meta():
    class MyMutation(Mutation):

        @classmethod
        def mutate(cls, *args, **kwargs):
            pass

    assert MyMutation._meta


def test_mutation_raises_exception_if_no_mutate():
    with pytest.raises(AssertionError) as excinfo:
        class MyMutation(Mutation):
            pass

    assert "All mutations must define a mutate method in it" == str(excinfo.value)

# def test_objecttype_inheritance():
#     class MyInheritedObjectType(ObjectType):
#         inherited = Field(GraphQLString)

#     class MyObjectType(MyInheritedObjectType):
#         field = Field(GraphQLString)

#     graphql_type = MyObjectType._meta.graphql_type
#     fields = graphql_type.get_fields()
#     assert 'field' in fields
#     assert 'inherited' in fields
#     assert fields['field'] > fields['inherited']


# def test_objecttype_as_container_only_args():
#     container = Container("1", "2")
#     assert container.field1 == "1"
#     assert container.field2 == "2"


# def test_objecttype_as_container_args_kwargs():
#     container = Container("1", field2="2")
#     assert container.field1 == "1"
#     assert container.field2 == "2"


# def test_objecttype_as_container_few_kwargs():
#     container = Container(field2="2")
#     assert container.field2 == "2"


# def test_objecttype_as_container_all_kwargs():
#     container = Container(field1="1", field2="2")
#     assert container.field1 == "1"
#     assert container.field2 == "2"


# def test_objecttype_as_container_extra_args():
#     with pytest.raises(IndexError) as excinfo:
#         Container("1", "2", "3")

#     assert "Number of args exceeds number of fields" == str(excinfo.value)


# def test_objecttype_as_container_invalid_kwargs():
#     with pytest.raises(TypeError) as excinfo:
#         Container(unexisting_field="3")

#     assert "'unexisting_field' is an invalid keyword argument for this function" == str(excinfo.value)


# def test_objecttype_reuse_graphql_type():
#     MyGraphQLType = GraphQLObjectType('MyGraphQLType', fields={
#         'field': GraphQLField(GraphQLString)
#     })

#     class GrapheneObjectType(ObjectType):
#         class Meta:
#             graphql_type = MyGraphQLType

#     graphql_type = GrapheneObjectType._meta.graphql_type
#     assert graphql_type == MyGraphQLType
#     instance = GrapheneObjectType(field="A")
#     assert instance.field == "A"


# def test_objecttype_add_fields_in_reused_graphql_type():
#     MyGraphQLType = GraphQLObjectType('MyGraphQLType', fields={
#         'field': GraphQLField(GraphQLString)
#     })

#     with pytest.raises(AssertionError) as excinfo:
#         class GrapheneObjectType(ObjectType):
#             field = Field(GraphQLString)

#             class Meta:
#                 graphql_type = MyGraphQLType

#     assert """Field "MyGraphQLType.field" can only be mounted in ObjectType or Interface, received GrapheneObjectType.""" == str(excinfo.value)


# def test_objecttype_graphql_interface():
#     MyInterface = GraphQLInterfaceType('MyInterface', fields={
#         'field': GraphQLField(GraphQLString)
#     })

#     class GrapheneObjectType(ObjectType):
#         class Meta:
#             interfaces = [MyInterface]

#     graphql_type = GrapheneObjectType._meta.graphql_type
#     assert graphql_type.get_interfaces() == (MyInterface, )
#     # assert graphql_type.is_type_of(MyInterface, None, None)
#     fields = graphql_type.get_fields()
#     assert 'field' in fields


# def test_objecttype_graphene_interface():
#     class GrapheneInterface(Interface):
#         field = Field(GraphQLString)

#     class GrapheneObjectType(ObjectType):
#         class Meta:
#             interfaces = [GrapheneInterface]

#     graphql_type = GrapheneObjectType._meta.graphql_type
#     assert graphql_type.get_interfaces() == (GrapheneInterface._meta.graphql_type, )
#     assert graphql_type.is_type_of(GrapheneObjectType(), None, None)
#     fields = graphql_type.get_fields()
#     assert 'field' in fields


# def test_objecttype_graphene_interface_extended():
#     class GrapheneInterface(Interface):
#         field = Field(GraphQLString)

#     class GrapheneObjectType(ObjectType):
#         class Meta:
#             interfaces = [GrapheneInterface]

#     schema = Schema(query=GrapheneObjectType)
#     assert str(schema) == """
# schema {
#   query: GrapheneObjectType
# }

# interface GrapheneInterface {
#   field: String
# }

# type GrapheneObjectType implements GrapheneInterface {
#   field: String
# }
# """.lstrip()
#     GrapheneInterface._meta.graphql_type.add_field(Field(String, name='dynamic'))
#     # GrapheneObjectType._meta.graphql_type._field_map = None
#     assert GrapheneInterface._meta.graphql_type.get_fields().keys() == ['field', 'dynamic']
#     assert GrapheneObjectType._meta.graphql_type.get_fields().keys() == ['field', 'dynamic']
#     schema.rebuild()
#     assert str(schema) == """
# schema {
#   query: GrapheneObjectType
# }

# interface GrapheneInterface {
#   field: String
#   dynamic: String
# }

# type GrapheneObjectType implements GrapheneInterface {
#   field: String
#   dynamic: String
# }
# """.lstrip()
