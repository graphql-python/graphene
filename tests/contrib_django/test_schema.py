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

from tests.utils import assert_equal_lists


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


def test_should_raise_if_model_is_invalid():
    with raises(Exception) as excinfo:
        class ReporterTypeError(DjangoObjectType):

            class Meta:
                model = Reporter
                only_fields = ('articles', )

        schema = graphene.Schema(query=ReporterTypeError)
        query = '''
            query ReporterQuery {
              articles
            }
        '''
        result = schema.execute(query)
        assert not result.errors


def test_should_map_fields_correctly():
    class ReporterType2(DjangoObjectType):

        class Meta:
            model = Reporter
    assert_equal_lists(
        ReporterType2._meta.fields_map.keys(),
        ['articles', 'first_name', 'last_name', 'email', 'pets', 'id']
    )


def test_should_map_fields():
    class ReporterType(DjangoObjectType):

        class Meta:
            model = Reporter

    class Query2(graphene.ObjectType):
        reporter = graphene.Field(ReporterType)

        def resolve_reporter(self, *args, **kwargs):
            return ReporterType(Reporter(first_name='ABA', last_name='X'))

    query = '''
        query ReporterQuery {
          reporter {
            firstName,
            lastName,
            email
          }
        }
    '''
    expected = {
        'reporter': {
            'firstName': 'ABA',
            'lastName': 'X',
            'email': ''
        }
    }
    Schema = graphene.Schema(query=Query2)
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_should_map_only_few_fields():
    class Reporter2(DjangoObjectType):

        class Meta:
            model = Reporter
            only_fields = ('id', 'email')
    assert_equal_lists(
        Reporter2._meta.fields_map.keys(),
        ['id', 'email']
    )


def test_should_node():
    class ReporterNodeType(DjangoNode):

        class Meta:
            model = Reporter

        @classmethod
        def get_node(cls, id):
            return ReporterNodeType(Reporter(id=2, first_name='Cookie Monster'))

        def resolve_articles(self, *args, **kwargs):
            return [ArticleNodeType(Article(headline='Hi!'))]

    class ArticleNodeType(DjangoNode):

        class Meta:
            model = Article

        @classmethod
        def get_node(cls, id):
            return ArticleNodeType(Article(id=1, headline='Article node'))

    class Query1(graphene.ObjectType):
        node = relay.NodeField()
        reporter = graphene.Field(ReporterNodeType)
        article = graphene.Field(ArticleNodeType)

        def resolve_reporter(self, *args, **kwargs):
            return ReporterNodeType(Reporter(id=1, first_name='ABA', last_name='X'))

    query = '''
        query ReporterQuery {
          reporter {
            id,
            firstName,
            articles {
              edges {
                node {
                  headline
                }
              }
            }
            lastName,
            email
          }
          myArticle: node(id:"QXJ0aWNsZU5vZGVUeXBlOjE=") {
            id
            ... on ReporterNodeType {
                firstName
            }
            ... on ArticleNodeType {
                headline
            }
          }
        }
    '''
    expected = {
        'reporter': {
            'id': 'UmVwb3J0ZXJOb2RlVHlwZTox',
            'firstName': 'ABA',
            'lastName': 'X',
            'email': '',
            'articles': {
                'edges': [{
                  'node': {
                      'headline': 'Hi!'
                  }
                }]
            },
        },
        'myArticle': {
            'id': 'QXJ0aWNsZU5vZGVUeXBlOjE=',
            'headline': 'Article node'
        }
    }
    Schema = graphene.Schema(query=Query1)
    result = Schema.execute(query)
    assert not result.errors
    assert result.data == expected
