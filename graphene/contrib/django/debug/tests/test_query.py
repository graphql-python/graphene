import pytest

import graphene
from graphene.contrib.django import DjangoObjectType

from ...tests.models import Reporter
from ..schema import DebugSchema

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
        all_reporters = ReporterType.List

        def resolve_all_reporters(self, *args, **kwargs):
            return Reporter.objects.all()

        def resolve_reporter(self, *args, **kwargs):
            return Reporter.objects.first()

    query = '''
        query ReporterQuery {
          reporter {
            lastName
          }
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
        'reporter': {
            'lastName': 'ABA',
        },
        'allReporters': [{
            'lastName': 'ABA',
        }, {
            'lastName': 'Griffin',
        }],
        '__debug': {
            'sql': [{
                'rawSql': str(Reporter.objects.order_by('pk')[:1].query)
            }, {
                'rawSql': str(Reporter.objects.all().query)
            }]
        }
    }
    schema = DebugSchema(query=Query)
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected
