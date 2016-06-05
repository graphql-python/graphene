import six

from graphql import GraphQLInputObjectType

from .definitions import ClassTypeMeta, GrapheneFieldsType, FieldMap
from .proxy import TypeProxy


class GrapheneInputObjectType(GrapheneFieldsType, GraphQLInputObjectType):
    pass


class InputObjectTypeMeta(ClassTypeMeta):

    def get_options(cls, meta):
        return cls.options_class(
            meta,
            name=None,
            description=None,
            graphql_type=None,
            abstract=False
        )

    def construct_graphql_type(cls, bases):
        if not cls._meta.graphql_type and not cls._meta.abstract:
            from ..utils.get_graphql_type import get_graphql_type
            from ..utils.is_graphene_type import is_graphene_type

            inherited_types = [
                base._meta.graphql_type for base in bases if is_graphene_type(base)
            ]

            cls._meta.graphql_type = GrapheneInputObjectType(
                graphene_type=cls,
                name=cls._meta.name or cls.__name__,
                description=cls._meta.description,
                fields=FieldMap(cls, bases=filter(None, inherited_types)),
            )


class InputObjectType(six.with_metaclass(InputObjectTypeMeta, TypeProxy)):
    class Meta:
        abstract = True
