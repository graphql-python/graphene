from graphene.contrib.django import settings

if not settings.GRAPHENE_ENABLE_FILTERING:
    raise Exception(
        "To make use of filtering you configure "
        "GRAPHENE_ENABLE_FILTERING=True. This will also require "
        "django-filter be installed"
    )

from .fields import DjangoFilterConnectionField
from .filterset import GrapheneFilterSet, GlobalIDFilter, GlobalIDMultipleChoiceFilter
from .resolvers import FilterConnectionResolver

__all__ = ['DjangoFilterConnectionField', 'GrapheneFilterSet',
           'GlobalIDFilter', 'GlobalIDMultipleChoiceFilter',
           'FilterConnectionResolver']
