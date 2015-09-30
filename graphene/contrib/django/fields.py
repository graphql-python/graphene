from graphene.core.fields import (
    ListField
)
from graphene import relay

from graphene.core.fields import Field, LazyField
from graphene.utils import cached_property
from graphene.env import get_global_schema

from django.db.models.query import QuerySet
from django.db.models.manager import Manager


def get_type_for_model(schema, model):
    schema = schema or get_global_schema()
    types = schema.types.values()
    for _type in types:
        type_model = hasattr(_type,'_meta') and getattr(_type._meta, 'model', None)
        if model == type_model:
            return _type


class DjangoConnectionField(relay.ConnectionField):
    def wrap_resolved(self, value, instance, args, info):
        if isinstance(value, (QuerySet, Manager)):
            cls = instance.__class__
            value = [cls(s) for s in value.all()]
        return value


class ConnectionOrListField(LazyField):
    def get_field(self):
        schema = self.schema
        model_field = self.field_type
        field_object_type = model_field.get_object_type()
        if field_object_type and issubclass(field_object_type, schema.Node):
            field = DjangoConnectionField(model_field)
        else:
            field = ListField(model_field)
        field.contribute_to_class(self.object_type, self.field_name)
        return field


class DjangoModelField(Field):
    def __init__(self, model, *args, **kwargs):
        super(DjangoModelField, self).__init__(None, *args, **kwargs)
        self.model = model

    @cached_property
    def type(self):
        _type = self.get_object_type()
        return _type and _type._meta.type

    def get_object_type(self):
        _type = get_type_for_model(self.schema, self.model)
        if not _type and self.object_type._meta.only_fields:
            # We will only raise the exception if the related field is specified in only_fields
            raise Exception("Field %s (%s) model not mapped in current schema" % (self, self.model._meta.object_name))
        
        return _type
