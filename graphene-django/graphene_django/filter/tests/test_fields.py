from datetime import datetime

import pytest

from graphene import ObjectType, Schema
from graphene.contrib.django import DjangoNode
from graphene.contrib.django.forms import (GlobalIDFormField,
                                           GlobalIDMultipleChoiceField)
from graphene.contrib.django.tests.models import Article, Pet, Reporter
from graphene.contrib.django.utils import DJANGO_FILTER_INSTALLED
from graphene.relay import NodeField

pytestmark = []
if DJANGO_FILTER_INSTALLED:
    import django_filters
    from graphene.contrib.django.filter import (GlobalIDFilter, DjangoFilterConnectionField,
                                                GlobalIDMultipleChoiceFilter)
    from graphene.contrib.django.filter.tests.filters import ArticleFilter, PetFilter
else:
    pytestmark.append(pytest.mark.skipif(True, reason='django_filters not installed'))

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

schema = Schema()


def assert_arguments(field, *arguments):
    ignore = ('after', 'before', 'first', 'last', 'orderBy')
    actual = [
        name
        for name in schema.T(field.arguments)
        if name not in ignore and not name.startswith('_')
    ]
    assert set(arguments) == set(actual), \
        'Expected arguments ({}) did not match actual ({})'.format(
            arguments,
            actual
    )


def assert_orderable(field):
    assert 'orderBy' in schema.T(field.arguments), \
        'Field cannot be ordered'


def assert_not_orderable(field):
    assert 'orderBy' not in schema.T(field.arguments), \
        'Field can be ordered'


def test_filter_explicit_filterset_arguments():
    field = DjangoFilterConnectionField(ArticleNode, filterset_class=ArticleFilter)
    assert_arguments(field,
                     'headline', 'headline_Icontains',
                     'pubDate', 'pubDate_Gt', 'pubDate_Lt',
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
                     'headline', 'headline_Icontains',
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
        'order_by': True
    })
    assert_orderable(field)


def test_filter_filterset_information_on_meta():
    class ReporterFilterNode(DjangoNode):

        class Meta:
            model = Reporter
            filter_fields = ['first_name', 'articles']
            filter_order_by = True

    field = DjangoFilterConnectionField(ReporterFilterNode)
    assert_arguments(field, 'firstName', 'articles')
    assert_orderable(field)


def test_filter_filterset_information_on_meta_related():
    class ReporterFilterNode(DjangoNode):

        class Meta:
            model = Reporter
            filter_fields = ['first_name', 'articles']
            filter_order_by = True

    class ArticleFilterNode(DjangoNode):

        class Meta:
            model = Article
            filter_fields = ['headline', 'reporter']
            filter_order_by = True

    class Query(ObjectType):
        all_reporters = DjangoFilterConnectionField(ReporterFilterNode)
        all_articles = DjangoFilterConnectionField(ArticleFilterNode)
        reporter = NodeField(ReporterFilterNode)
        article = NodeField(ArticleFilterNode)

    schema = Schema(query=Query)
    schema.schema  # Trigger the schema loading
    articles_field = schema.get_type('ReporterFilterNode')._meta.fields_map['articles']
    assert_arguments(articles_field, 'headline', 'reporter')
    assert_orderable(articles_field)


def test_filter_filterset_related_results():
    class ReporterFilterNode(DjangoNode):

        class Meta:
            model = Reporter
            filter_fields = ['first_name', 'articles']
            filter_order_by = True

    class ArticleFilterNode(DjangoNode):

        class Meta:
            model = Article
            filter_fields = ['headline', 'reporter']
            filter_order_by = True

    class Query(ObjectType):
        all_reporters = DjangoFilterConnectionField(ReporterFilterNode)
        all_articles = DjangoFilterConnectionField(ArticleFilterNode)
        reporter = NodeField(ReporterFilterNode)
        article = NodeField(ArticleFilterNode)

    r1 = Reporter.objects.create(first_name='r1', last_name='r1', email='r1@test.com')
    r2 = Reporter.objects.create(first_name='r2', last_name='r2', email='r2@test.com')
    Article.objects.create(headline='a1', pub_date=datetime.now(), reporter=r1)
    Article.objects.create(headline='a2', pub_date=datetime.now(), reporter=r2)

    query = '''
    query {
        allReporters {
            edges {
                node {
                    articles {
                        edges {
                            node {
                                headline
                            }
                        }
                    }
                }
            }
        }
    }
    '''
    schema = Schema(query=Query)
    result = schema.execute(query)
    assert not result.errors
    # We should only get back a single article for each reporter
    assert len(result.data['allReporters']['edges'][0]['node']['articles']['edges']) == 1
    assert len(result.data['allReporters']['edges'][1]['node']['articles']['edges']) == 1


def test_global_id_field_implicit():
    field = DjangoFilterConnectionField(ArticleNode, fields=['id'])
    filterset_class = field.filterset_class
    id_filter = filterset_class.base_filters['id']
    assert isinstance(id_filter, GlobalIDFilter)
    assert id_filter.field_class == GlobalIDFormField


def test_global_id_field_explicit():
    class ArticleIdFilter(django_filters.FilterSet):

        class Meta:
            model = Article
            fields = ['id']

    field = DjangoFilterConnectionField(ArticleNode, filterset_class=ArticleIdFilter)
    filterset_class = field.filterset_class
    id_filter = filterset_class.base_filters['id']
    assert isinstance(id_filter, GlobalIDFilter)
    assert id_filter.field_class == GlobalIDFormField


def test_global_id_field_relation():
    field = DjangoFilterConnectionField(ArticleNode, fields=['reporter'])
    filterset_class = field.filterset_class
    id_filter = filterset_class.base_filters['reporter']
    assert isinstance(id_filter, GlobalIDFilter)
    assert id_filter.field_class == GlobalIDFormField


def test_global_id_multiple_field_implicit():
    field = DjangoFilterConnectionField(ReporterNode, fields=['pets'])
    filterset_class = field.filterset_class
    multiple_filter = filterset_class.base_filters['pets']
    assert isinstance(multiple_filter, GlobalIDMultipleChoiceFilter)
    assert multiple_filter.field_class == GlobalIDMultipleChoiceField


def test_global_id_multiple_field_explicit():
    class ReporterPetsFilter(django_filters.FilterSet):

        class Meta:
            model = Reporter
            fields = ['pets']

    field = DjangoFilterConnectionField(ReporterNode, filterset_class=ReporterPetsFilter)
    filterset_class = field.filterset_class
    multiple_filter = filterset_class.base_filters['pets']
    assert isinstance(multiple_filter, GlobalIDMultipleChoiceFilter)
    assert multiple_filter.field_class == GlobalIDMultipleChoiceField


def test_global_id_multiple_field_implicit_reverse():
    field = DjangoFilterConnectionField(ReporterNode, fields=['articles'])
    filterset_class = field.filterset_class
    multiple_filter = filterset_class.base_filters['articles']
    assert isinstance(multiple_filter, GlobalIDMultipleChoiceFilter)
    assert multiple_filter.field_class == GlobalIDMultipleChoiceField


def test_global_id_multiple_field_explicit_reverse():
    class ReporterPetsFilter(django_filters.FilterSet):

        class Meta:
            model = Reporter
            fields = ['articles']

    field = DjangoFilterConnectionField(ReporterNode, filterset_class=ReporterPetsFilter)
    filterset_class = field.filterset_class
    multiple_filter = filterset_class.base_filters['articles']
    assert isinstance(multiple_filter, GlobalIDMultipleChoiceFilter)
    assert multiple_filter.field_class == GlobalIDMultipleChoiceField
