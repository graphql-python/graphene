from py.test import raises
from collections import namedtuple
from pytest import raises
from graphene.core.fields import (
    Field,
    StringField,
)
from graphql.core.type import (
    GraphQLObjectType,
    GraphQLInterfaceType
)

from graphene import Schema
from graphene.contrib.django.types import (
    DjangoNode,
    DjangoInterface
)

from .models import Reporter, Article


class Character(DjangoInterface):

    '''Character description'''
    class Meta:
        model = Reporter


class Human(DjangoNode):

    '''Human description'''

    def get_node(self, id):
        pass

    class Meta:
        model = Article

schema = Schema()


def test_django_interface():
    assert DjangoNode._meta.interface is True


def test_pseudo_interface():
    object_type = Character.internal_type(schema)
    assert Character._meta.interface is True
    assert isinstance(object_type, GraphQLInterfaceType)
    assert Character._meta.model == Reporter
    assert object_type.get_fields().keys() == [
        'lastName', 'email', 'id', 'firstName', 'articles']


def test_interface_resolve_type():
    resolve_type = Character.resolve_type(schema, Human(object()))
    assert isinstance(resolve_type, GraphQLObjectType)


def test_object_type():
    object_type = Human.internal_type(schema)
    internal_fields_map = Human._meta.internal_fields_map
    assert Human._meta.interface is False
    assert isinstance(object_type, GraphQLObjectType)
    assert object_type.get_fields() == {
        'headline': internal_fields_map['headline'].internal_field(schema),
        'id': internal_fields_map['id'].internal_field(schema),
        'reporter': internal_fields_map['reporter'].internal_field(schema),
        'pubDate': internal_fields_map['pubDate'].internal_field(schema),
    }
    assert object_type.get_interfaces() == [DjangoNode.internal_type(schema)]
