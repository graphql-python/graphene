import pytest

import graphene
from graphene.contrib.django import DjangoObjectType

from ..tests.models import Reporter
from ..debug.plugin import DjangoDebugPlugin
from ..fetcher import fetch_only_required, get_fields

# from examples.starwars_django.models import Character

pytestmark = pytest.mark.django_db


def test_should_query_well():
    r1 = Reporter(last_name='ABA')
    r1.save()
    r2 = Reporter(last_name='Griffin')
    r2.save()

    class ReporterType(DjangoObjectType):

        class Meta:
            model = Reporter

    class Query(graphene.ObjectType):
        reporter = graphene.Field(ReporterType)
        all_reporters = ReporterType.List()

        @fetch_only_required
        def resolve_all_reporters(self, args, info):
            return Reporter.objects.all()

        def resolve_reporter(self, args, info):
            return Reporter.objects.only(*get_fields(info)).first()

    query = '''
        query ReporterQuery {
          allReporters {
            lastName
            email
          }
          reporter {
            email
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
            'email': '',
        }, {
            'lastName': 'Griffin',
            'email': '',
        }],
        'reporter': {
            'email': ''
        },
        '__debug': {
            'sql': [{
                'rawSql': str(Reporter.objects.all().only('last_name', 'email').query)
            }, {
                'rawSql': str(Reporter.objects.only('email').order_by('pk')[:1].query)
            }]
        }
    }
    schema = graphene.Schema(query=Query, plugins=[DjangoDebugPlugin()])
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected
