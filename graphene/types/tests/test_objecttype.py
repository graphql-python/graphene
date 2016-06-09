import pytest

from graphql import GraphQLObjectType, GraphQLField, GraphQLString, GraphQLInterfaceType

from ..schema import Schema
from ..objecttype import ObjectType
from ..interface import Interface
from ..scalars import String
from ..field import Field


class Container(ObjectType):
    field1 = Field(GraphQLString, name='field1')
    field2 = Field(GraphQLString, name='field2')


def test_generate_objecttype():
    class MyObjectType(ObjectType):
        '''Documentation'''
        pass

    graphql_type = MyObjectType._meta.graphql_type
    assert isinstance(graphql_type, GraphQLObjectType)
    assert graphql_type.name == "MyObjectType"
    assert graphql_type.description == "Documentation"


def test_generate_objecttype_with_meta():
    class MyObjectType(ObjectType):
        class Meta:
            name = 'MyOtherObjectType'
            description = 'Documentation'

    graphql_type = MyObjectType._meta.graphql_type
    assert isinstance(graphql_type, GraphQLObjectType)
    assert graphql_type.name == "MyOtherObjectType"
    assert graphql_type.description == "Documentation"


def test_empty_objecttype_has_meta():
    class MyObjectType(ObjectType):
        pass

    assert MyObjectType._meta


def test_generate_objecttype_with_fields():
    class MyObjectType(ObjectType):
        field = Field(GraphQLString)

    graphql_type = MyObjectType._meta.graphql_type
    fields = graphql_type.get_fields()
    assert 'field' in fields


def test_ordered_fields_in_objecttype():
    class MyObjectType(ObjectType):
        b = Field(GraphQLString)
        a = Field(GraphQLString)
        field = Field(GraphQLString)
        asa = Field(GraphQLString)

    graphql_type = MyObjectType._meta.graphql_type
    fields = graphql_type.get_fields()
    assert fields.keys() == ['b', 'a', 'field', 'asa']


def test_objecttype_inheritance():
    class MyInheritedObjectType(ObjectType):
        inherited = Field(GraphQLString)

    class MyObjectType(MyInheritedObjectType):
        field1 = Field(GraphQLString)
        field2 = Field(GraphQLString)

    graphql_type = MyObjectType._meta.graphql_type
    fields = graphql_type.get_fields()
    assert 'field1' in fields
    assert 'field2' in fields
    assert 'inherited' in fields
    assert fields['field1'] > fields['inherited']
    assert fields['field2'] > fields['field1']


def test_objecttype_as_container_get_fields():

    class Container(ObjectType):
        field1 = Field(GraphQLString)
        field2 = Field(GraphQLString)

    assert Container._meta.graphql_type.get_fields().keys() == ['field1', 'field2']


def test_parent_container_get_fields():
    fields = Container._meta.graphql_type.get_fields()
    print [(f.creation_counter, f.name) for f in fields.values()]
    assert fields.keys() == ['field1', 'field2']


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
#         name = Field(GraphQLString)
#         extended = Field(GraphQLString)

#     class GrapheneObjectType(ObjectType):
#         class Meta:
#             interfaces = [GrapheneInterface]

#         field = Field(GraphQLString)

#     graphql_type = GrapheneObjectType._meta.graphql_type
#     assert graphql_type.get_interfaces() == (GrapheneInterface._meta.graphql_type, )
#     assert graphql_type.is_type_of(GrapheneObjectType(), None, None)
#     fields = graphql_type.get_fields()
#     assert 'field' in fields
#     assert 'extended' in fields
#     assert 'name' in fields
#     assert fields['field'] > fields['extended'] > fields['name']


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
