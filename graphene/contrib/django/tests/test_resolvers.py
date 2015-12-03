from django.db.models import Manager
from django.db.models.query import QuerySet

from graphene.contrib.django import DjangoNode
from graphene.contrib.django.resolvers import SimpleQuerySetConnectionResolver
from graphene.contrib.django.tests.models import Reporter


class ReporterNode(DjangoNode):
    class Meta:
        model = Reporter


def test_simple_resolve():
    reporter = Reporter(id=1, first_name='Cookie Monster')
    resolver = SimpleQuerySetConnectionResolver(ReporterNode, on='articles')
    resolved = resolver(inst=reporter, args={}, info=None)
    assert isinstance(resolved, QuerySet), 'Did not resolve to a queryset'


def test_simple_get_manager_related():
    reporter = Reporter(id=1, first_name='Cookie Monster')
    resolver = SimpleQuerySetConnectionResolver(ReporterNode, on='articles')
    resolver(inst=reporter, args={}, info=None)
    assert resolver.get_manager().instance == reporter, 'Resolver did not return a RelatedManager'


def test_simple_get_manager_all():
    reporter = Reporter(id=1, first_name='Cookie Monster')
    resolver = SimpleQuerySetConnectionResolver(ReporterNode)
    resolver(inst=reporter, args={}, info=None)
    assert type(resolver.get_manager()) == Manager, 'Resolver did not return a Manager'


def test_simple_filter():
    reporter = Reporter(id=1, first_name='Cookie Monster')
    resolver = SimpleQuerySetConnectionResolver(ReporterNode)
    resolved = resolver(inst=reporter, args={
        'first_name': 'Elmo'
    }, info=None)
    assert '"first_name" = Elmo' in str(resolved.query)
    assert 'ORDER BY' not in str(resolved.query)


def test_simple_order():
    reporter = Reporter(id=1, first_name='Cookie Monster')
    resolver = SimpleQuerySetConnectionResolver(ReporterNode)
    resolved = resolver(inst=reporter, args={
        'order': 'last_name'
    }, info=None)
    assert 'WHERE' not in str(resolved.query)
    assert 'ORDER BY' in str(resolved.query)
    assert '"last_name" ASC' in str(resolved.query)
