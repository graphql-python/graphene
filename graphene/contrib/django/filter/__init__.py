from graphene.contrib.django.utils import DJANGO_FILTER_INSTALLED

if not DJANGO_FILTER_INSTALLED:
    raise Exception(
        "Use of django filtering requires the django-filter package "
        "be installed. You can do so using `pip install django-filter`"
    )

from .fields import DjangoFilterConnectionField
from .filterset import GrapheneFilterSet, GlobalIDFilter, GlobalIDMultipleChoiceFilter

__all__ = ['DjangoFilterConnectionField', 'GrapheneFilterSet',
           'GlobalIDFilter', 'GlobalIDMultipleChoiceFilter']
