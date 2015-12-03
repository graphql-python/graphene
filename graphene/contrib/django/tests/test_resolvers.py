from django.core.exceptions import ImproperlyConfigured
from py.test import raises
from django.db.models import Manager
from django.db.models.query import QuerySet

from graphene.contrib.django import DjangoNode
from graphene.contrib.django.resolvers import SimpleQuerySetConnectionResolver, FilterConnectionResolver
from graphene.contrib.django.tests.filters import ReporterFilter, ArticleFilter
from graphene.contrib.django.tests.models import Reporter, Article


class ReporterNode(DjangoNode):
    class Meta:
        model = Reporter


class ArticleNode(DjangoNode):
    class Meta:
        model = Article


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


def test_filter_get_filterset_class_explicit():
    reporter = Reporter(id=1, first_name='Cookie Monster')
    resolver = FilterConnectionResolver(ReporterNode,
                                        filterset_class=ReporterFilter)
    resolver(inst=reporter, args={}, info=None)
    assert issubclass(resolver.get_filterset_class(), ReporterFilter), \
        'ReporterFilter not returned'


def test_filter_get_filterset_class_implicit():
    reporter = Reporter(id=1, first_name='Cookie Monster')
    resolver = FilterConnectionResolver(ReporterNode)
    resolver(inst=reporter, args={}, info=None)
    assert resolver.get_filterset_class().__name__ == 'ReporterFilterSet'


def test_filter_get_filterset_class_error():
    reporter = Reporter(id=1, first_name='Cookie Monster')
    resolver = FilterConnectionResolver(ReporterNode)
    resolver.model = None
    with raises(ImproperlyConfigured) as excinfo:
        resolver(inst=reporter, args={}, info=None)
    assert "Neither 'filterset_class' or 'model' available" in str(excinfo.value)


def test_filter_filter():
    reporter = Reporter(id=1, first_name='Cookie Monster')
    resolver = FilterConnectionResolver(ReporterNode,
                                        filterset_class=ReporterFilter)
    resolved = resolver(inst=reporter, args={
        'first_name': 'Elmo'
    }, info=None)
    assert '"first_name" = Elmo' in str(resolved.query)
    assert 'ORDER BY' not in str(resolved.query)


def test_filter_filter_contains():
    article = Article(id=1, headline='Cookie Monster eats fruit')
    resolver = FilterConnectionResolver(ArticleNode,
                                        filterset_class=ArticleFilter)
    resolved = resolver(inst=article, args={
        'headline__icontains': 'Elmo'
    }, info=None)
    assert '"headline" LIKE %Elmo%' in str(resolved.query)


def test_filter_order():
    article = Article(id=1, headline='Cookie Monster eats fruit')
    resolver = FilterConnectionResolver(ArticleNode,
                                        filterset_class=ArticleFilter)
    resolved = resolver(inst=article, args={
        # TODO: This should be 'order', not 'o'
        'o': 'headline'
    }, info=None)
    assert 'WHERE' not in str(resolved.query)
    assert 'ORDER BY' in str(resolved.query)
    assert '"headline" ASC' in str(resolved.query)


def test_filter_order_not_available():
    reporter = Reporter(id=1, first_name='Cookie Monster')
    resolver = FilterConnectionResolver(ReporterNode,
                                        filterset_class=ReporterFilter)
    resolved = resolver(inst=reporter, args={
        # TODO: This should be 'order', not 'o'
        'o': 'last_name'
    }, info=None)
    assert 'WHERE' not in str(resolved.query)
    assert 'ORDER BY' not in str(resolved.query)
