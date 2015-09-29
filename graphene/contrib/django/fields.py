from graphene.core.fields import Field
from graphene.utils import cached_property

from graphene.env import get_global_schema


def get_type_for_model(schema, model):
    schema = schema or get_global_schema()
    types = schema.types.values()
    for _type in types:
        type_model = getattr(_type._meta, 'model', None)
        if model == type_model:
            return _type


class DjangoModelField(Field):
    def __init__(self, model):
        super(DjangoModelField, self).__init__(None)
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
