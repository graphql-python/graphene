from functools import wraps
from graphql.core.utils.get_field_def import get_field_def
import pytest

import graphene
from graphene.contrib.django import DjangoObjectType

from graphql.core.type.definition import GraphQLList, GraphQLNonNull


from ..tests.models import Reporter
from ..debug.plugin import DjangoDebugPlugin

# from examples.starwars_django.models import Character

pytestmark = pytest.mark.django_db

def get_fields(info):
    field_asts = info.field_asts[0].selection_set.selections
    only_args = []
    _type = info.return_type
    if isinstance(_type, (GraphQLList, GraphQLNonNull)):
        _type = _type.of_type

    for field in field_asts:
        field_def = get_field_def(info.schema, _type, field)
        f = field_def.resolver
        fetch_field = getattr(f, 'django_fetch_field', None)
        if fetch_field:
            only_args.append(fetch_field)
    return only_args

def fetch_only_required(f):
    @wraps(f)
    def wrapper(*args):
        info = args[-1]
        return f(*args).only(*get_fields(info))
    return wrapper

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
