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
    assert DjangoNode._meta.interface == True


def test_pseudo_interface():
    object_type = Character.internal_type(schema)
    assert Character._meta.interface == True
    assert isinstance(object_type, GraphQLInterfaceType)
    assert Character._meta.model == Reporter
    assert object_type.get_fields().keys() == [
        'articles', 'first_name', 'last_name', 'id', 'email']


def test_interface_resolve_type():
    resolve_type = Character.resolve_type(schema, Human(object()))
    assert isinstance(resolve_type, GraphQLObjectType)


def test_object_type():
    object_type = Human.internal_type(schema)
    assert Human._meta.interface == False
    assert isinstance(object_type, GraphQLObjectType)
    assert object_type.get_fields() == {
        'headline': Human._meta.fields_map['headline'].internal_field(schema),
        'id': Human._meta.fields_map['id'].internal_field(schema),
        'reporter': Human._meta.fields_map['reporter'].internal_field(schema),
        'pub_date': Human._meta.fields_map['pub_date'].internal_field(schema),
    }
    assert object_type.get_interfaces() == [DjangoNode.internal_type(schema)]
