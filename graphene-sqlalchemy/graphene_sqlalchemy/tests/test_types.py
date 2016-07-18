from graphql.type import GraphQLObjectType
from pytest import raises

from graphene import Schema
from graphene.contrib.sqlalchemy.types import (SQLAlchemyNode,
                                               SQLAlchemyObjectType)
from graphene.core.fields import Field
from graphene.core.types.scalars import Int
from graphene.relay.fields import GlobalIDField
from tests.utils import assert_equal_lists

from .models import Article, Reporter

schema = Schema()


class Character(SQLAlchemyObjectType):
    '''Character description'''
    class Meta:
        model = Reporter


@schema.register
class Human(SQLAlchemyNode):
    '''Human description'''

    pub_date = Int()

    class Meta:
        model = Article
        exclude_fields = ('id', )


def test_sqlalchemy_interface():
    assert SQLAlchemyNode._meta.interface is True


# @patch('graphene.contrib.sqlalchemy.tests.models.Article.filter', return_value=Article(id=1))
# def test_sqlalchemy_get_node(get):
#     human = Human.get_node(1, None)
#     get.assert_called_with(id=1)
#     assert human.id == 1


def test_objecttype_registered():
    object_type = schema.T(Character)
    assert isinstance(object_type, GraphQLObjectType)
    assert Character._meta.model == Reporter
    assert_equal_lists(
        object_type.get_fields().keys(),
        ['articles', 'firstName', 'lastName', 'email', 'id']
    )


def test_sqlalchemynode_idfield():
    idfield = SQLAlchemyNode._meta.fields_map['id']
    assert isinstance(idfield, GlobalIDField)


def test_node_idfield():
    idfield = Human._meta.fields_map['id']
    assert isinstance(idfield, GlobalIDField)


def test_node_replacedfield():
    idfield = Human._meta.fields_map['pub_date']
    assert isinstance(idfield, Field)
    assert schema.T(idfield).type == schema.T(Int())


def test_interface_objecttype_init_none():
    h = Human()
    assert h._root is None


def test_interface_objecttype_init_good():
    instance = Article()
    h = Human(instance)
    assert h._root == instance


def test_interface_objecttype_init_unexpected():
    with raises(AssertionError) as excinfo:
        Human(object())
    assert str(excinfo.value) == "Human received a non-compatible instance (object) when expecting Article"


def test_object_type():
    object_type = schema.T(Human)
    Human._meta.fields_map
    assert Human._meta.interface is False
    assert isinstance(object_type, GraphQLObjectType)
    assert_equal_lists(
        object_type.get_fields().keys(),
        ['headline', 'id', 'reporter', 'reporterId', 'pubDate']
    )
    assert schema.T(SQLAlchemyNode) in object_type.get_interfaces()


def test_node_notinterface():
    assert Human._meta.interface is False
    assert SQLAlchemyNode in Human._meta.interfaces
