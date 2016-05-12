from functools import partial

import six
from graphql.type import GraphQLUnionType

from .base import FieldsClassType, FieldsClassTypeMeta, FieldsOptions


class UnionTypeOptions(FieldsOptions):

    def __init__(self, *args, **kwargs):
        super(UnionTypeOptions, self).__init__(*args, **kwargs)
        self.types = []


class UnionTypeMeta(FieldsClassTypeMeta):
    options_class = UnionTypeOptions

    def get_options(cls, meta):
        return cls.options_class(meta, types=[])


class UnionType(six.with_metaclass(UnionTypeMeta, FieldsClassType)):

    class Meta:
        abstract = True

    @classmethod
    def _resolve_type(cls, schema, instance, *args):
        return schema.T(instance.__class__)

    @classmethod
    def internal_type(cls, schema):
        if cls._meta.abstract:
            raise Exception("Abstract ObjectTypes don't have a specific type.")

        return GraphQLUnionType(
            cls._meta.type_name,
            types=list(map(schema.T, cls._meta.types)),
            resolve_type=partial(cls._resolve_type, schema),
            description=cls._meta.description,
        )
