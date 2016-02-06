import pytest

import graphene
from graphene.contrib.django import DjangoNode, DjangoConnectionField
from graphene.contrib.django.filter import DjangoFilterConnectionField

from ...tests.models import Reporter
from ..plugin import DjangoDebugPlugin

# from examples.starwars_django.models import Character

from django.db.models import Count

pytestmark = pytest.mark.django_db


def count(qs):
    query = qs.query
    query.add_annotation(Count('*'), alias='__count', is_summary=True)
    query.select = []
    query.default_cols = False
    return query


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

        def resolve_all_reporters_connection(self, *args, **kwargs):
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
        '__debug': {
            'sql': [{
                'rawSql': str(count(Reporter.objects.all()))
            }, {
                'rawSql': str(Reporter.objects.all()[:1].query)
            }]
        }
    }
    schema = graphene.Schema(query=Query, plugins=[DjangoDebugPlugin()])
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_should_query_connectionfilter():
    r1 = Reporter(last_name='ABA')
    r1.save()
    r2 = Reporter(last_name='Griffin')
    r2.save()

    class ReporterType(DjangoNode):

        class Meta:
            model = Reporter

    class Query(graphene.ObjectType):
        all_reporters = DjangoFilterConnectionField(ReporterType)

        def resolve_all_reporters_connection_filter(self, *args, **kwargs):
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
        '__debug': {
            'sql': [{
                'rawSql': str(count(Reporter.objects.all()))
            }, {
                'rawSql': str(Reporter.objects.all()[:1].query)
            }]
        }
    }
    schema = graphene.Schema(query=Query, plugins=[DjangoDebugPlugin()])
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected
