import pytest
from django.core.exceptions import ImproperlyConfigured

try:
    import django_filters  # noqa
except ImportError:
    pytestmark = pytest.mark.skipif(True, reason='django_filters not installed')
else:
    from graphene.contrib.django.filter.resolvers import FilterConnectionResolver
    from graphene.contrib.django.tests.filter.filters import ReporterFilter, ArticleFilter

from graphene.contrib.django.tests.models import Reporter, Article
from graphene.contrib.django.tests.test_resolvers import ReporterNode, ArticleNode


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
    with pytest.raises(ImproperlyConfigured) as excinfo:
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
        'order_by': 'headline'
    }, info=None)
    assert 'WHERE' not in str(resolved.query)
    assert 'ORDER BY' in str(resolved.query)
    assert '"headline" ASC' in str(resolved.query)


def test_filter_order_not_available():
    reporter = Reporter(id=1, first_name='Cookie Monster')
    resolver = FilterConnectionResolver(ReporterNode,
                                        filterset_class=ReporterFilter)
    resolved = resolver(inst=reporter, args={
        'order_by': 'last_name'
    }, info=None)
    assert 'WHERE' not in str(resolved.query)
    assert 'ORDER BY' not in str(resolved.query)
