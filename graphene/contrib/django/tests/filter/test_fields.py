import pytest
from django.apps import apps
from django.conf import settings

pytestmark = []

try:
    import django_filters
except ImportError:
    pytestmark.append(pytest.mark.skipif(True, reason='django_filters not installed'))
else:
    from graphene.contrib.django.filter import (GlobalIDFilter, DjangoFilterConnectionField,
                                                GlobalIDMultipleChoiceFilter)
    from graphene.contrib.django.tests.filter.filters import ArticleFilter, PetFilter

from graphene.contrib.django import DjangoNode
from graphene.contrib.django.forms import GlobalIDFormField, GlobalIDMultipleChoiceField
from graphene.contrib.django.tests.models import Article, Pet, Reporter

# settings.INSTALLED_APPS.append('graphene.contrib.django.tests')
# apps.set_installed_apps(settings.INSTALLED_APPS)

pytestmark.append(pytest.mark.django_db)


class ArticleNode(DjangoNode):
    class Meta:
        model = Article


class ReporterNode(DjangoNode):
    class Meta:
        model = Reporter


class PetNode(DjangoNode):
    class Meta:
        model = Pet


def assert_arguments(field, *arguments):
    ignore = ('after', 'before', 'first', 'last', 'order')
    actual = [
        name
        for name in field.arguments.arguments.keys()
        if name not in ignore and not name.startswith('_')
    ]
    assert set(arguments) == set(actual), \
        'Expected arguments ({}) did not match actual ({})'.format(
            arguments,
            actual
        )


def assert_orderable(field):
    assert 'order' in field.arguments.arguments.keys(), \
        'Field cannot be ordered'


def assert_not_orderable(field):
    assert 'order' in field.arguments.arguments.keys(), \
        'Field can be ordered'


def test_filter_explicit_filterset_arguments():
    field = DjangoFilterConnectionField(ArticleNode, filterset_class=ArticleFilter)
    assert_arguments(field,
                     'headline', 'headlineIcontains',
                     'pubDate', 'pubDateGt', 'pubDateLt',
                     'reporter',
                     )


def test_filter_shortcut_filterset_arguments_list():
    field = DjangoFilterConnectionField(ArticleNode, fields=['pub_date', 'reporter'])
    assert_arguments(field,
                     'pubDate',
                     'reporter',
                     )


def test_filter_shortcut_filterset_arguments_dict():
    field = DjangoFilterConnectionField(ArticleNode, fields={
        'headline': ['exact', 'icontains'],
        'reporter': ['exact'],
    })
    assert_arguments(field,
                     'headline', 'headlineIcontains',
                     'reporter',
                     )


def test_filter_explicit_filterset_orderable():
    field = DjangoFilterConnectionField(ArticleNode, filterset_class=ArticleFilter)
    assert_orderable(field)


def test_filter_shortcut_filterset_orderable_true():
    field = DjangoFilterConnectionField(ArticleNode, order_by=True)
    assert_orderable(field)


def test_filter_shortcut_filterset_orderable_headline():
    field = DjangoFilterConnectionField(ArticleNode, order_by=['headline'])
    assert_orderable(field)


def test_filter_explicit_filterset_not_orderable():
    field = DjangoFilterConnectionField(PetNode, filterset_class=PetFilter)
    assert_not_orderable(field)


def test_filter_shortcut_filterset_extra_meta():
    field = DjangoFilterConnectionField(ArticleNode, extra_filter_meta={
        'ordering': True
    })
    assert_orderable(field)


def test_global_id_field_implicit():
    field = DjangoFilterConnectionField(ArticleNode, fields=['id'])
    filterset_class = field.resolver_fn.get_filterset_class()
    id_filter = filterset_class.base_filters['id']
    assert isinstance(id_filter, GlobalIDFilter)
    assert id_filter.field_class == GlobalIDFormField


def test_global_id_field_explicit():
    class ArticleIdFilter(django_filters.FilterSet):
        class Meta:
            model = Article
            fields = ['id']

    field = DjangoFilterConnectionField(ArticleNode, filterset_class=ArticleIdFilter)
    filterset_class = field.resolver_fn.get_filterset_class()
    id_filter = filterset_class.base_filters['id']
    assert isinstance(id_filter, GlobalIDFilter)
    assert id_filter.field_class == GlobalIDFormField


def test_global_id_field_relation():
    field = DjangoFilterConnectionField(ArticleNode, fields=['reporter'])
    filterset_class = field.resolver_fn.get_filterset_class()
    id_filter = filterset_class.base_filters['reporter']
    assert isinstance(id_filter, GlobalIDFilter)
    assert id_filter.field_class == GlobalIDFormField


def test_global_id_multiple_field_implicit():
    field = DjangoFilterConnectionField(ReporterNode, fields=['pets'])
    filterset_class = field.resolver_fn.get_filterset_class()
    multiple_filter = filterset_class.base_filters['pets']
    assert isinstance(multiple_filter, GlobalIDMultipleChoiceFilter)
    assert multiple_filter.field_class == GlobalIDMultipleChoiceField


def test_global_id_multiple_field_explicit():
    class ReporterPetsFilter(django_filters.FilterSet):
        class Meta:
            model = Reporter
            fields = ['pets']

    field = DjangoFilterConnectionField(ReporterNode, filterset_class=ReporterPetsFilter)
    filterset_class = field.resolver_fn.get_filterset_class()
    multiple_filter = filterset_class.base_filters['pets']
    assert isinstance(multiple_filter, GlobalIDMultipleChoiceFilter)
    assert multiple_filter.field_class == GlobalIDMultipleChoiceField


def test_global_id_multiple_field_implicit_reverse():
    field = DjangoFilterConnectionField(ReporterNode, fields=['articles'])
    filterset_class = field.resolver_fn.get_filterset_class()
    multiple_filter = filterset_class.base_filters['articles']
    assert isinstance(multiple_filter, GlobalIDMultipleChoiceFilter)
    assert multiple_filter.field_class == GlobalIDMultipleChoiceField


def test_global_id_multiple_field_explicit_reverse():
    Reporter._meta.get_field("articles")
    class ReporterPetsFilter(django_filters.FilterSet):
        class Meta:
            model = Reporter
            fields = ['articles']

    field = DjangoFilterConnectionField(ReporterNode, filterset_class=ReporterPetsFilter)
    filterset_class = field.resolver_fn.get_filterset_class()
    multiple_filter = filterset_class.base_filters['articles']
    assert isinstance(multiple_filter, GlobalIDMultipleChoiceFilter)
    assert multiple_filter.field_class == GlobalIDMultipleChoiceField
