import pytest

import graphene
from graphene.contrib.django import DjangoConnectionField, DjangoNode
from graphene.contrib.django.utils import DJANGO_FILTER_INSTALLED

from ...tests.models import Reporter
from ..plugin import DjangoDebugPlugin

# from examples.starwars_django.models import Character

pytestmark = pytest.mark.django_db


def test_should_query_field():
    r1 = Reporter(last_name='ABA')
    r1.save()
    r2 = Reporter(last_name='Griffin')
    r2.save()

    class ReporterType(DjangoNode):

        class Meta:
            model = Reporter

    class Query(graphene.ObjectType):
        reporter = graphene.Field(ReporterType)

        def resolve_reporter(self, *args, **kwargs):
            return Reporter.objects.first()

    query = '''
        query ReporterQuery {
          reporter {
            lastName
          }
          __debug {
            sql {
              rawSql
            }
          }
        }
    '''
    expected = {
        'reporter': {
            'lastName': 'ABA',
        },
        '__debug': {
            'sql': [{
                'rawSql': str(Reporter.objects.order_by('pk')[:1].query)
            }]
        }
    }
    schema = graphene.Schema(query=Query, plugins=[DjangoDebugPlugin()])
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_should_query_list():
    r1 = Reporter(last_name='ABA')
    r1.save()
    r2 = Reporter(last_name='Griffin')
    r2.save()

    class ReporterType(DjangoNode):

        class Meta:
            model = Reporter

    class Query(graphene.ObjectType):
        all_reporters = ReporterType.List()

        def resolve_all_reporters(self, *args, **kwargs):
            return Reporter.objects.all()

    query = '''
        query ReporterQuery {
          allReporters {
            lastName
          }
          __debug {
            sql {
              rawSql
            }
          }
        }
    '''
    expected = {
        'allReporters': [{
            'lastName': 'ABA',
        }, {
            'lastName': 'Griffin',
        }],
        '__debug': {
            'sql': [{
                'rawSql': str(Reporter.objects.all().query)
            }]
        }
    }
    schema = graphene.Schema(query=Query, plugins=[DjangoDebugPlugin()])
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_should_query_connection():
    r1 = Reporter(last_name='ABA')
    r1.save()
    r2 = Reporter(last_name='Griffin')
    r2.save()

    class ReporterType(DjangoNode):

        class Meta:
            model = Reporter

    class Query(graphene.ObjectType):
        all_reporters = DjangoConnectionField(ReporterType)

        def resolve_all_reporters(self, *args, **kwargs):
            return Reporter.objects.all()

    query = '''
        query ReporterQuery {
          allReporters(first:1) {
            edges {
              node {
                lastName
              }
            }
          }
          __debug {
            sql {
              rawSql
            }
          }
        }
    '''
    expected = {
        'allReporters': {
            'edges': [{
                'node': {
                    'lastName': 'ABA',
                }
            }]
        },
    }
    schema = graphene.Schema(query=Query, plugins=[DjangoDebugPlugin()])
    result = schema.execute(query)
    assert not result.errors
    assert result.data['allReporters'] == expected['allReporters']
    assert 'COUNT' in result.data['__debug']['sql'][0]['rawSql']
    query = str(Reporter.objects.all()[:1].query)
    assert result.data['__debug']['sql'][1]['rawSql'] == query


@pytest.mark.skipif(not DJANGO_FILTER_INSTALLED,
                    reason="requires django-filter")
def test_should_query_connectionfilter():
    from graphene.contrib.django.filter import DjangoFilterConnectionField

    r1 = Reporter(last_name='ABA')
    r1.save()
    r2 = Reporter(last_name='Griffin')
    r2.save()

    class ReporterType(DjangoNode):

        class Meta:
            model = Reporter

    class Query(graphene.ObjectType):
        all_reporters = DjangoFilterConnectionField(ReporterType)

        def resolve_all_reporters(self, *args, **kwargs):
            return Reporter.objects.all()

    query = '''
        query ReporterQuery {
          allReporters(first:1) {
            edges {
              node {
                lastName
              }
            }
          }
          __debug {
            sql {
              rawSql
            }
          }
        }
    '''
    expected = {
        'allReporters': {
            'edges': [{
                'node': {
                    'lastName': 'ABA',
                }
            }]
        },
    }
    schema = graphene.Schema(query=Query, plugins=[DjangoDebugPlugin()])
    result = schema.execute(query)
    assert not result.errors
    assert result.data['allReporters'] == expected['allReporters']
    assert 'COUNT' in result.data['__debug']['sql'][0]['rawSql']
    query = str(Reporter.objects.all()[:1].query)
    assert result.data['__debug']['sql'][1]['rawSql'] == query
