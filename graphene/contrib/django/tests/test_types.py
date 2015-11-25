from graphql.core.type import GraphQLInterfaceType, GraphQLObjectType
from mock import patch
from pytest import raises

from graphene import Schema
from graphene.contrib.django.types import DjangoInterface, DjangoNode
from graphene.core.fields import Field
from graphene.core.types.scalars import Int
from graphene.relay.fields import GlobalIDField
from tests.utils import assert_equal_lists

from .models import Article, Reporter

schema = Schema()


class Character(DjangoInterface):
    '''Character description'''
    class Meta:
        model = Reporter


@schema.register
class Human(DjangoNode):
    '''Human description'''

    pub_date = Int()

    class Meta:
        model = Article


def test_django_interface():
    assert DjangoNode._meta.is_interface is True


@patch('graphene.contrib.django.tests.models.Article.objects.get', return_value=Article(id=1))
def test_django_get_node(get):
    human = Human.get_node(1, None)
    get.assert_called_with(id=1)
    assert human.id == 1


def test_pseudo_interface_registered():
    object_type = schema.T(Character)
    assert Character._meta.is_interface is True
    assert isinstance(object_type, GraphQLInterfaceType)
    assert Character._meta.model == Reporter
    assert_equal_lists(
        object_type.get_fields().keys(),
        ['articles', 'firstName', 'lastName', 'email', 'pets', 'id']
    )


def test_djangonode_idfield():
    idfield = DjangoNode._meta.fields_map['id']
    assert isinstance(idfield, GlobalIDField)


def test_node_idfield():
    idfield = Human._meta.fields_map['id']
    assert isinstance(idfield, GlobalIDField)


def test_node_replacedfield():
    idfield = Human._meta.fields_map['pub_date']
    assert isinstance(idfield, Field)
    assert schema.T(idfield).type == schema.T(Int())


def test_interface_resolve_type():
    resolve_type = Character._resolve_type(schema, Human())
    assert isinstance(resolve_type, GraphQLObjectType)


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
    assert Human._meta.is_interface is False
    assert isinstance(object_type, GraphQLObjectType)
    assert_equal_lists(
        object_type.get_fields().keys(),
        ['headline', 'id', 'reporter', 'pubDate']
    )
    assert schema.T(DjangoNode) in object_type.get_interfaces()


def test_node_notinterface():
    assert Human._meta.is_interface is False
    assert DjangoNode in Human._meta.interfaces
