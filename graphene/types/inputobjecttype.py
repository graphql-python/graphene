import six

from graphql import GraphQLInputObjectType

from .definitions import FieldsMeta, ClassTypeMeta, GrapheneFieldsType
from .proxy import TypeProxy


class GrapheneInputObjectType(GrapheneFieldsType, GraphQLInputObjectType):
    pass


class InputObjectTypeMeta(FieldsMeta, ClassTypeMeta):

    def get_options(cls, meta):
        return cls.options_class(
            meta,
            name=None,
            description=None,
            graphql_type=None,
            abstract=False
        )

    def construct_graphql_type(cls, bases):
        pass

    def construct(cls, bases, attrs):
        if not cls._meta.graphql_type and not cls._meta.abstract:
            cls._meta.graphql_type = GrapheneInputObjectType(
                graphene_type=cls,
                name=cls._meta.name or cls.__name__,
                description=cls._meta.description or cls.__doc__,
                fields=cls._fields(bases, attrs),
            )
        return super(InputObjectTypeMeta, cls).construct(bases, attrs)


class InputObjectType(six.with_metaclass(InputObjectTypeMeta, TypeProxy)):
    class Meta:
        abstract = True
