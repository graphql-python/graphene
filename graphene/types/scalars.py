import six
from graphql import GraphQLScalarType, GraphQLString, GraphQLInt, GraphQLFloat, GraphQLBoolean, GraphQLID

from .definitions import GrapheneGraphQLType
from .unmountedtype import UnmountedType
from .options import Options
from ..utils.is_base_type import is_base_type


class GrapheneScalarType(GrapheneGraphQLType, GraphQLScalarType):
    pass


class ScalarTypeMeta(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(ScalarTypeMeta, cls).__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, ScalarTypeMeta):
            return super_new(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=None,
            description=None,
            graphql_type=None
        )

        cls = super_new(cls, name, bases, dict(attrs, _meta=options))

        if not options.graphql_type:
            options.graphql_type = GrapheneScalarType(
                graphene_type=cls,
                name=cls._meta.name or cls.__name__,
                description=cls._meta.description or cls.__doc__,

                serialize=getattr(cls, 'serialize', None),
                parse_value=getattr(cls, 'parse_value', None),
                parse_literal=getattr(cls, 'parse_literal', None),
            )

        return cls


class Scalar(six.with_metaclass(ScalarTypeMeta, UnmountedType)):
    pass


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
