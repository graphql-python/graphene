import six
from graphql import GraphQLScalarType, GraphQLString, GraphQLInt, GraphQLFloat, GraphQLBoolean, GraphQLID

from .definitions import ClassTypeMeta, GrapheneGraphQLType
from .unmountedtype import UnmountedType


class GrapheneScalarType(GrapheneGraphQLType, GraphQLScalarType):
    pass


class ScalarTypeMeta(ClassTypeMeta):

    def get_options(cls, meta):
        return cls.options_class(
            meta,
            name=None,
            description=None,
            graphql_type=None,
            abstract=False
        )

    def construct(cls, *args, **kwargs):
        constructed = super(ScalarTypeMeta, cls).construct(*args, **kwargs)
        if not cls._meta.graphql_type and not cls._meta.abstract:
            cls._meta.graphql_type = GrapheneScalarType(
                graphene_type=cls,
                name=cls._meta.name or cls.__name__,
                description=cls._meta.description or cls.__doc__,

                serialize=getattr(cls, 'serialize', None),
                parse_value=getattr(cls, 'parse_value', None),
                parse_literal=getattr(cls, 'parse_literal', None),
            )

        return constructed


class Scalar(six.with_metaclass(ScalarTypeMeta, UnmountedType)):
    class Meta:
        abstract = True


def construct_scalar_class(graphql_type):
    # This is equivalent to
    # class String(Scalar):
    #     class Meta:
    #         graphql_type = graphql_type
    Meta = type('Meta', (object,), {'graphql_type':graphql_type})
    return type(graphql_type.name, (Scalar, ), {'Meta': Meta})


String = construct_scalar_class(GraphQLString)
Int = construct_scalar_class(GraphQLInt)
Float = construct_scalar_class(GraphQLFloat)
Boolean = construct_scalar_class(GraphQLBoolean)
ID = construct_scalar_class(GraphQLID)
