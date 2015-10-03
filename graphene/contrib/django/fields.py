from graphene.core.fields import (
    ListField
)
from graphene import relay

from graphene.core.fields import Field, LazyField
from graphene.utils import cached_property, memoize, LazyMap

from graphene.relay.types import BaseNode

from django.db.models.query import QuerySet
from django.db.models.manager import Manager


@memoize
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
        schema = info.schema.graphene_schema
        return lazy_map(value, self.get_object_type(schema))


class LazyListField(ListField):
    def resolve(self, instance, args, info):
        schema = info.schema.graphene_schema
        resolved = super(LazyListField, self).resolve(instance, args, info)
        return lazy_map(resolved, self.get_object_type(schema))


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
        if not _type and self.object_type._meta.only_fields:
            raise Exception(
                "Model %r is not accessible by the schema. "
                "You can either register the type manually "
                "using @schema.register. "
                "Or disable the field %s in %s" % (
                    self.model,
                    self.field_name,
                    self.object_type
                )
            )
        return _type and _type.internal_type(schema) or Field.SKIP

    def get_object_type(self, schema):
        return get_type_for_model(schema, self.model)
