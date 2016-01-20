from django.db import models
from django.db.models.manager import Manager
from django.db.models.query import QuerySet

from graphene.utils import LazyList

from .compat import RelatedObject

try:
    import django_filters  # noqa
    DJANGO_FILTER_INSTALLED = True
except (ImportError, AttributeError):
    # AtributeError raised if DjangoFilters installed with a incompatible Django Version
    DJANGO_FILTER_INSTALLED = False


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
        # Django =>1.9 uses 'rel', django <1.9 uses 'related'
        related = getattr(attr, 'rel', None) or \
            getattr(attr, 'related', None)
        if isinstance(related, RelatedObject):
            # Hack for making it compatible with Django 1.6
            new_related = RelatedObject(related.parent_model, related.model, related.field)
            new_related.name = name
            yield new_related
        elif isinstance(related, models.ManyToOneRel):
            yield related
        elif isinstance(related, models.ManyToManyRel) and not related.symmetrical:
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


def get_related_model(field):
    if hasattr(field, 'rel'):
        # Django 1.6, 1.7
        return field.rel.to
    return field.related_model


def import_single_dispatch():
    try:
        from functools import singledispatch
    except ImportError:
        singledispatch = None

    if not singledispatch:
        try:
            from singledispatch import singledispatch
        except ImportError:
            pass

    if not singledispatch:
        raise Exception(
            "It seems your python version does not include "
            "functools.singledispatch. Please install the 'singledispatch' "
            "package. More information here: "
            "https://pypi.python.org/pypi/singledispatch"
        )

    return singledispatch
