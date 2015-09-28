from py.test import raises
from collections import namedtuple
from pytest import raises
import graphene
from graphene import relay
from graphene.contrib.django import (
    DjangoObjectType,
    DjangoNode
)
from .models import Reporter, Article


def test_should_raise_if_no_model():
    with raises(Exception) as excinfo:
        class Character1(DjangoObjectType):
            pass
    assert 'model in the Meta' in str(excinfo.value)


def test_should_raise_if_model_is_invalid():
    with raises(Exception) as excinfo:
        class Character2(DjangoObjectType):
            class Meta:
                model = 1
    assert 'not a Django model' in str(excinfo.value)


def test_should_map_fields():
    class ReporterType(DjangoObjectType):
        class Meta:
            model = Reporter

    class Query(graphene.ObjectType):
        reporter = graphene.Field(ReporterType)

        def resolve_reporter(self, *args, **kwargs):
            return ReporterType(Reporter(first_name='ABA', last_name='X'))

    query = '''
        query ReporterQuery {
          reporter {
            first_name,
            last_name,
            email
          }
        }
    '''
    expected = {
        'reporter': {
            'first_name': 'ABA',
            'last_name': 'X',
            'email': ''
        }
    }
    Schema = graphene.Schema(query=Query)
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_should_map_only_few_fields():
    class Reporter2(DjangoObjectType):
        class Meta:
            model = Reporter
            only_fields = ('id', 'email')
    assert Reporter2._meta.fields_map.keys() == ['id', 'email']

def test_should_node():
    class ReporterNodeType(DjangoNode):
        class Meta:
            model = Reporter

        @classmethod
        def get_node(cls, id):
            return ReporterNodeType(Reporter(id=2, first_name='Cookie Monster'))

    class ArticleNodeType(DjangoNode):
        class Meta:
            model = Article

        @classmethod
        def get_node(cls, id):
            return ArticleNodeType(None)

    class Query(graphene.ObjectType):
        node = relay.NodeField()
        reporter = graphene.Field(ReporterNodeType)

        def resolve_reporter(self, *args, **kwargs):
            return ReporterNodeType(Reporter(id=1, first_name='ABA', last_name='X'))

    query = '''
        query ReporterQuery {
          reporter {
            id,
            first_name,
            last_name,
            email
          }
          aCustomNode: node(id:"UmVwb3J0ZXJOb2RlVHlwZToy") {
            id
            ... on ReporterNodeType {
                first_name
            }
          }
        }
    '''
    expected = {
        'reporter': {
            'id': 'UmVwb3J0ZXJOb2RlVHlwZTox',
            'first_name': 'ABA',
            'last_name': 'X',
            'email': ''
        },
        'aCustomNode': {
            'id': 'UmVwb3J0ZXJOb2RlVHlwZToy',
            'first_name': 'Cookie Monster'
        }
    }
    Schema = graphene.Schema(query=Query)
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected
