from django.db import models
from django.db.models.manager import Manager
from django.db.models.query import QuerySet

from graphene.utils import LazyList


def get_type_for_model(schema, model):
    schema = schema
    types = schema.types.values()
    for _type in types:
        type_model = hasattr(_type, '_meta') and getattr(
            _type._meta, 'model', None)
        if model == type_model:
            return _type


def get_reverse_fields(model):
    for name, attr in model.__dict__.items():
        related = getattr(attr, 'related', None)
        if isinstance(related, models.ManyToOneRel):
            yield related


class WrappedQueryset(LazyList):

    def __len__(self):
        # Dont calculate the length using len(queryset), as this will
        # evaluate the whole queryset and return it's length.
        # Use .count() instead
        return self._origin.count()


def maybe_queryset(value):
    if isinstance(value, Manager):
        value = value.get_queryset()
    if isinstance(value, QuerySet):
        return WrappedQueryset(value)
    return value
