from graphene import Schema
from graphene.contrib.django import DjangoFilterConnectionField, DjangoNode
from graphene.contrib.django.tests.filters import ArticleFilter, PetFilter
from graphene.contrib.django.tests.models import Article, Pet

schema = Schema()


@schema.register
class ArticleNode(DjangoNode):

    class Meta:
        model = Article


@schema.register
class PetNode(DjangoNode):

    class Meta:
        model = Pet


def assert_arguments(field, *arguments):
    ignore = ('after', 'before', 'first', 'last', 'o')
    actual = [
        name
        for name in field.arguments.arguments.keys()
        if name not in ignore and not name.startswith('_')
    ]
    assert set(arguments) == set(actual), \
        'Expected arguments ({}) did not match actual ({])'.format(
            arguments,
            actual
        )


def assert_orderable(field):
    assert 'o' in field.arguments.arguments.keys(), \
        'Field cannot be ordered'


def assert_not_orderable(field):
    assert 'o' in field.arguments.arguments.keys(), \
        'Field cannot be ordered'


def test_filter_explicit_filterset_arguments():
    field = DjangoFilterConnectionField(ArticleNode, filterset_class=ArticleFilter)
    assert_arguments(field,
                     'headline', 'headlineIcontains',
                     'pubDate', 'pubDateGt', 'pubDateLt',
                     'reporter',
                     )


def test_filter_explicit_filterset_orderable():
    field = DjangoFilterConnectionField(ArticleNode, filterset_class=ArticleFilter)
    assert_orderable(field)


def test_filter_explicit_filterset_not_orderable():
    field = DjangoFilterConnectionField(PetNode, filterset_class=PetFilter)
    assert_not_orderable(field)
