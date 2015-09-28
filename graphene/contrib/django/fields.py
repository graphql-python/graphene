from graphene.core.fields import Field
from graphene.utils import cached_property

from graphene.env import get_global_schema


def get_type_for_model(schema, model):
    schema = schema or get_global_schema()
    types = schema.types.values()
    for _type in types:
        type_model = getattr(_type._meta, 'model', None)
        if model == type_model:
            return _type._meta.type


class DjangoModelField(Field):
    def __init__(self, model):
        super(DjangoModelField, self).__init__(None)
        self.model = model

    @cached_property
    def type(self):
        return get_type_for_model(self.schema, self.model)
