from functools import partial

from graphql.type import GraphQLInputObjectType

from .base import FieldsClassType


class InputObjectType(FieldsClassType):

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        raise Exception("An InputObjectType cannot be initialized")

    @classmethod
    def internal_type(cls, schema):
        if cls._meta.abstract:
            raise Exception("Abstract InputObjectTypes don't have a specific type.")

        return GraphQLInputObjectType(
            cls._meta.type_name,
            description=cls._meta.description,
            fields=partial(cls.fields_internal_types, schema),
        )
