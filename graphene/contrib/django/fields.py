from graphene.core.fields import (
    ListField
)
from graphene import relay

from graphene.core.fields import Field, LazyField
from graphene.utils import cached_property, memoize, LazyMap

from graphene.relay.types import BaseNode

from django.db.models.query import QuerySet
from django.db.models.manager import Manager


def get_type_for_model(schema, model):
    schema = schema
    types = schema.types.values()
    for _type in types:
        type_model = hasattr(_type, '_meta') and getattr(
            _type._meta, 'model', None)
        if model == type_model:
            return _type


def lazy_map(value, func):
    if isinstance(value, Manager):
        value = value.get_queryset()
    if isinstance(value, QuerySet):
        return LazyMap(value, func)
    return value


class DjangoConnectionField(relay.ConnectionField):
    def wrap_resolved(self, value, instance, args, info):
        return lazy_map(value, instance.__class__)


class LazyListField(ListField):
    def resolve(self, value, instance, args, info):
        resolved = super(LazyListField, self).resolve(value, instance, args, info)
        return lazy_map(resolved, instance.__class__)


class ConnectionOrListField(LazyField):
    @memoize
    def get_field(self, schema):
        model_field = self.field_type
        field_object_type = model_field.get_object_type(schema)
        if field_object_type and issubclass(field_object_type, BaseNode):
            field = DjangoConnectionField(model_field)
        else:
            field = LazyListField(model_field)
        field.contribute_to_class(self.object_type, self.name)
        return field


class DjangoModelField(Field):
    def __init__(self, model, *args, **kwargs):
        super(DjangoModelField, self).__init__(None, *args, **kwargs)
        self.model = model

    @memoize
    def internal_type(self, schema):
        _type = self.get_object_type(schema)
        return _type and _type.internal_type(schema)

    def get_object_type(self, schema):
        _type = get_type_for_model(schema, self.model)
        if not _type and self.object_type._meta.only_fields:
            # We will only raise the exception if the related field is
            # specified in only_fields
            raise Exception("Field %s (%s) model not mapped in current schema" % (
                self, self.model._meta.object_name))

        return _type
