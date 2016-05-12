from graphql.type import GraphQLObjectType
from mock import patch

from graphene import Schema
from graphene.contrib.django.types import DjangoNode, DjangoObjectType
from graphene.core.fields import Field
from graphene.core.types.scalars import Int
from graphene.relay.fields import GlobalIDField
from tests.utils import assert_equal_lists

from .models import Article, Reporter

schema = Schema()


@schema.register
class Character(DjangoObjectType):
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
    assert DjangoNode._meta.interface is True


@patch('graphene.contrib.django.tests.models.Article.objects.get', return_value=Article(id=1))
def test_django_get_node(get):
    human = Human.get_node(1, None)
    get.assert_called_with(id=1)
    assert human.id == 1


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


def test_objecttype_init_none():
    h = Human()
    assert h._root is None


def test_objecttype_init_good():
    instance = Article()
    h = Human(instance)
    assert h._root == instance


def test_object_type():
    object_type = schema.T(Human)
    Human._meta.fields_map
    assert Human._meta.interface is False
    assert isinstance(object_type, GraphQLObjectType)
    assert_equal_lists(
        object_type.get_fields().keys(),
        ['headline', 'id', 'reporter', 'pubDate']
    )
    assert schema.T(DjangoNode) in object_type.get_interfaces()


def test_node_notinterface():
    assert Human._meta.interface is False
    assert DjangoNode in Human._meta.interfaces
