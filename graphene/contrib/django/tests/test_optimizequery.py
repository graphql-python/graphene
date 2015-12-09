from graphql.core.utils.get_field_def import get_field_def
import pytest

import graphene
from graphene.contrib.django import DjangoObjectType

from ..tests.models import Reporter
from ..debug.plugin import DjangoDebugPlugin

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

        def resolve_all_reporters(self, args, info):
            queryset = Reporter.objects.all()
            # from graphql.core.execution.base import collect_fields
            # print info.field_asts[0], info.parent_type, info.return_type.of_type
            # field_asts = collect_fields(info.context, info.parent_type, info.field_asts[0], {}, set())
            # field_asts = info.field_asts
            field_asts = info.field_asts[0].selection_set.selections
            only_args = []
            for field in field_asts:
                field_def = get_field_def(info.schema, info.return_type.of_type, field)
                f = field_def.resolver
                fetch_field = getattr(f, 'django_fetch_field')
                only_args.append(fetch_field)
            queryset = queryset.only(*only_args)
            return queryset

        def resolve_reporter(self, *args, **kwargs):
            return Reporter.objects.first()

    query = '''
        query ReporterQuery {
          allReporters {
            lastName
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
        '__debug': {
            'sql': [{
                'rawSql': str(Reporter.objects.all().only('last_name', 'email').query)
            }]
        }
    }
    schema = graphene.Schema(query=Query, plugins=[DjangoDebugPlugin()])
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected
