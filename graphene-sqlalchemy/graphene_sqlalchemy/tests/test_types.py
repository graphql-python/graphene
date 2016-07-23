from graphql.type import GraphQLObjectType, GraphQLInterfaceType
from graphql.type.definition import GraphQLFieldDefinition
from graphql import GraphQLInt
from pytest import raises

from graphene import Schema
from ..types import (SQLAlchemyNode, SQLAlchemyObjectType)
from ..registry import Registry

from graphene import Field, Int
# from tests.utils import assert_equal_lists

from .models import Article, Reporter

registry = Registry()

class Character(SQLAlchemyObjectType):
    '''Character description'''
    class Meta:
        model = Reporter
        registry = registry


class Human(SQLAlchemyNode, SQLAlchemyObjectType):
    '''Human description'''

    pub_date = Int()

    class Meta:
        model = Article
        exclude = ('id', )
        registry = registry





def test_sqlalchemy_interface():
    assert isinstance(SQLAlchemyNode._meta.graphql_type, GraphQLInterfaceType)


# @patch('graphene.contrib.sqlalchemy.tests.models.Article.filter', return_value=Article(id=1))
# def test_sqlalchemy_get_node(get):
#     human = Human.get_node(1, None)
#     get.assert_called_with(id=1)
#     assert human.id == 1


def test_objecttype_registered():
    object_type = Character._meta.graphql_type
    assert isinstance(object_type, GraphQLObjectType)
    assert Character._meta.model == Reporter
    assert object_type.get_fields().keys() == ['articles', 'id', 'firstName', 'lastName', 'email']


# def test_sqlalchemynode_idfield():
#     idfield = SQLAlchemyNode._meta.fields_map['id']
#     assert isinstance(idfield, GlobalIDField)


# def test_node_idfield():
#     idfield = Human._meta.fields_map['id']
#     assert isinstance(idfield, GlobalIDField)


def test_node_replacedfield():
    idfield = Human._meta.graphql_type.get_fields()['pubDate']
    assert isinstance(idfield, GraphQLFieldDefinition)
    assert idfield.type == GraphQLInt


def test_object_type():
    object_type = Human._meta.graphql_type
    object_type.get_fields()
    assert isinstance(object_type, GraphQLObjectType)
    assert object_type.get_fields().keys() == ['id', 'pubDate', 'reporter', 'headline', 'reporterId']
    assert SQLAlchemyNode._meta.graphql_type in object_type.get_interfaces()
