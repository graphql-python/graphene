from collections import OrderedDict

from py.test import raises

from ..objecttype import ObjectType
from ..interface import Interface
from ..union import Union
from ..scalars import String, Int, Boolean
from ..field import Field
from ..structures import List

from ..schema import Schema


class Image(ObjectType):
    url = String()
    width = Int()
    height = Int()


class Author(ObjectType):
    id = String()
    name = String()
    pic = Field(Image)  # width=Int(), height=Int()
    recent_article = Field(lambda: Article)


class Article(ObjectType):
    id = String()
    is_published = Boolean()
    author = Field(Author)
    title = String()
    body = String()


class Query(ObjectType):
    article = Field(Article)  # id=String()
    feed = List(Article)


class Mutation(ObjectType):
    write_article = Field(Article)


class Subscription(ObjectType):
    article_subscribe = Field(Article)  # id=String()


class MyInterface(Interface):
    pass


class MyUnion(Union):
    class Meta:
        types = (Article, )


def test_defines_a_query_only_schema():
    blog_schema = Schema(Query)

    assert blog_schema.get_query_type().graphene_type == Query

    article_field = Query._meta.fields['article']
    assert article_field.type == Article
    assert article_field.type._meta.name == 'Article'

    article_field_type = article_field.type
    assert issubclass(article_field_type, ObjectType)

    title_field = article_field_type._meta.fields['title']
    assert title_field.type == String

    author_field = article_field_type._meta.fields['author']
    author_field_type = author_field.type
    assert issubclass(author_field_type, ObjectType)
    recent_article_field = author_field_type._meta.fields['recent_article']

    assert recent_article_field.type == Article

    feed_field = Query._meta.fields['feed']
    assert feed_field.type.of_type == Article


def test_defines_a_mutation_schema():
    blog_schema = Schema(Query, mutation=Mutation)

    assert blog_schema.get_mutation_type().graphene_type == Mutation

    write_mutation = Mutation._meta.fields['write_article']
    assert write_mutation.type == Article
    assert write_mutation.type._meta.name == 'Article'


def test_defines_a_subscription_schema():
    blog_schema = Schema(Query, subscription=Subscription)

    assert blog_schema.get_subscription_type().graphene_type == Subscription

    subscription = Subscription._meta.fields['article_subscribe']
    assert subscription.type == Article
    assert subscription.type._meta.name == 'Article'


# def test_includes_nested_input_objects_in_the_map():
#     NestedInputObject = GraphQLInputObjectType(
#         name='NestedInputObject',
#         fields={'value': GraphQLInputObjectField(GraphQLString)}
#     )

#     SomeInputObject = GraphQLInputObjectType(
#         name='SomeInputObject',
#         fields={'nested': GraphQLInputObjectField(NestedInputObject)}
#     )

#     SomeMutation = GraphQLObjectType(
#         name='SomeMutation',
#         fields={
#             'mutateSomething': GraphQLField(
#                 type=BlogArticle,
#                 args={
#                     'input': GraphQLArgument(SomeInputObject)
#                 }
#             )
#         }
#     )
#     SomeSubscription = GraphQLObjectType(
#         name='SomeSubscription',
#         fields={
#             'subscribeToSomething': GraphQLField(
#                 type=BlogArticle,
#                 args={
#                     'input': GraphQLArgument(SomeInputObject)
#                 }
#             )
#         }
#     )

#     schema = GraphQLSchema(
#         query=BlogQuery,
#         mutation=SomeMutation,
#         subscription=SomeSubscription
#     )

#     assert schema.get_type_map()['NestedInputObject'] is NestedInputObject


# def test_includes_interfaces_thunk_subtypes_in_the_type_map():
#     SomeInterface = GraphQLInterfaceType(
#         name='SomeInterface',
#         fields={
#             'f': GraphQLField(GraphQLInt)
#         }
#     )

#     SomeSubtype = GraphQLObjectType(
#         name='SomeSubtype',
#         fields={
#             'f': GraphQLField(GraphQLInt)
#         },
#         interfaces=lambda: [SomeInterface],
#         is_type_of=lambda: True
#     )

#     schema = GraphQLSchema(query=GraphQLObjectType(
#         name='Query',
#         fields={
#             'iface': GraphQLField(SomeInterface)
#         }
#     ), types=[SomeSubtype])

#     assert schema.get_type_map()['SomeSubtype'] is SomeSubtype


# def test_includes_interfaces_subtypes_in_the_type_map():
#     SomeInterface = GraphQLInterfaceType('SomeInterface', fields={'f': GraphQLField(GraphQLInt)})
#     SomeSubtype = GraphQLObjectType(
#         name='SomeSubtype',
#         fields={'f': GraphQLField(GraphQLInt)},
#         interfaces=[SomeInterface],
#         is_type_of=lambda: None
#     )
#     schema = GraphQLSchema(
#         query=GraphQLObjectType(
#             name='Query',
#             fields={
#                 'iface': GraphQLField(SomeInterface)}),
#         types=[SomeSubtype])
#     assert schema.get_type_map()['SomeSubtype'] == SomeSubtype


def test_stringifies_simple_types():
    assert str(Int) == 'Int'
    assert str(Article) == 'Article'
    assert str(MyInterface) == 'MyInterface'
    assert str(MyUnion) == 'MyUnion'
    # assert str(EnumType) == 'Enum'
    # assert str(InputObjectType) == 'InputObject'
    # assert str(GraphQLNonNull(GraphQLInt)) == 'Int!'
    # assert str(GraphQLList(GraphQLInt)) == '[Int]'
    # assert str(GraphQLNonNull(GraphQLList(GraphQLInt))) == '[Int]!'
    # assert str(GraphQLList(GraphQLNonNull(GraphQLInt))) == '[Int!]'
    # assert str(GraphQLList(GraphQLList(GraphQLInt))) == '[[Int]]'


# def test_identifies_input_types():
#     expected = (
#         (GraphQLInt, True),
#         (ObjectType, False),
#         (InterfaceType, False),
#         (UnionType, False),
#         (EnumType, True),
#         (InputObjectType, True)
#     )

#     for type, answer in expected:
#         assert is_input_type(type) == answer
#         assert is_input_type(GraphQLList(type)) == answer
#         assert is_input_type(GraphQLNonNull(type)) == answer


# def test_identifies_output_types():
#     expected = (
#         (GraphQLInt, True),
#         (ObjectType, True),
#         (InterfaceType, True),
#         (UnionType, True),
#         (EnumType, True),
#         (InputObjectType, False)
#     )

#     for type, answer in expected:
#         assert is_output_type(type) == answer
#         assert is_output_type(GraphQLList(type)) == answer
#         assert is_output_type(GraphQLNonNull(type)) == answer


# def test_prohibits_nesting_nonnull_inside_nonnull():
#     with raises(Exception) as excinfo:
#         GraphQLNonNull(GraphQLNonNull(GraphQLInt))

#     assert 'Can only create NonNull of a Nullable GraphQLType but got: Int!.' in str(excinfo.value)


# def test_prohibits_putting_non_object_types_in_unions():
#     bad_union_types = [
#         GraphQLInt,
#         GraphQLNonNull(GraphQLInt),
#         GraphQLList(GraphQLInt),
#         InterfaceType,
#         UnionType,
#         EnumType,
#         InputObjectType
#     ]
#     for x in bad_union_types:
#         with raises(Exception) as excinfo:
#             GraphQLSchema(GraphQLObjectType('Root', fields={'union': GraphQLField(GraphQLUnionType('BadUnion', [x]))}))

#         assert 'BadUnion may only contain Object types, it cannot contain: ' + str(x) + '.' \
#                == str(excinfo.value)


# def test_does_not_mutate_passed_field_definitions():
#     fields = {
#         'field1': GraphQLField(GraphQLString),
#         'field2': GraphQLField(GraphQLString, args={'id': GraphQLArgument(GraphQLString)}),
#     }

#     TestObject1 = GraphQLObjectType(name='Test1', fields=fields)
#     TestObject2 = GraphQLObjectType(name='Test1', fields=fields)

#     assert TestObject1.get_fields() == TestObject2.get_fields()
#     assert fields == {
#         'field1': GraphQLField(GraphQLString),
#         'field2': GraphQLField(GraphQLString, args={'id': GraphQLArgument(GraphQLString)}),
#     }

#     input_fields = {
#         'field1': GraphQLInputObjectField(GraphQLString),
#         'field2': GraphQLInputObjectField(GraphQLString),
#     }

#     TestInputObject1 = GraphQLInputObjectType(name='Test1', fields=input_fields)
#     TestInputObject2 = GraphQLInputObjectType(name='Test2', fields=input_fields)

#     assert TestInputObject1.get_fields() == TestInputObject2.get_fields()

#     assert input_fields == {
#         'field1': GraphQLInputObjectField(GraphQLString),
#         'field2': GraphQLInputObjectField(GraphQLString),
#     }


# def test_sorts_fields_and_argument_keys_if_not_using_ordered_dict():
#     fields = {
#         'b': GraphQLField(GraphQLString),
#         'c': GraphQLField(GraphQLString),
#         'a': GraphQLField(GraphQLString),
#         'd': GraphQLField(GraphQLString, args={
#             'q': GraphQLArgument(GraphQLString),
#             'x': GraphQLArgument(GraphQLString),
#             'v': GraphQLArgument(GraphQLString),
#             'a': GraphQLArgument(GraphQLString),
#             'n': GraphQLArgument(GraphQLString)
#         })
#     }

#     test_object = GraphQLObjectType(name='Test', fields=fields)
#     ordered_fields = test_object.get_fields()
#     assert list(ordered_fields.keys()) == ['a', 'b', 'c', 'd']
#     field_with_args = test_object.get_fields().get('d')
#     assert [a.name for a in field_with_args.args] == ['a', 'n', 'q', 'v', 'x']


# def test_does_not_sort_fields_and_argument_keys_when_using_ordered_dict():
#     fields = OrderedDict([
#         ('b', GraphQLField(GraphQLString)),
#         ('c', GraphQLField(GraphQLString)),
#         ('a', GraphQLField(GraphQLString)),
#         ('d', GraphQLField(GraphQLString, args=OrderedDict([
#             ('q', GraphQLArgument(GraphQLString)),
#             ('x', GraphQLArgument(GraphQLString)),
#             ('v', GraphQLArgument(GraphQLString)),
#             ('a', GraphQLArgument(GraphQLString)),
#             ('n', GraphQLArgument(GraphQLString))
#         ])))
#     ])

#     test_object = GraphQLObjectType(name='Test', fields=fields)
#     ordered_fields = test_object.get_fields()
#     assert list(ordered_fields.keys()) == ['b', 'c', 'a', 'd']
#     field_with_args = test_object.get_fields().get('d')
#     assert [a.name for a in field_with_args.args] == ['q', 'x', 'v', 'a', 'n']
