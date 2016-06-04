import six
from graphql import GraphQLString, GraphQLInt, GraphQLFloat, GraphQLBoolean, GraphQLID

from .definitions import ClassTypeMeta, GrapheneScalarType
from .proxy import TypeProxy


class ScalarTypeMeta(ClassTypeMeta):

    def get_options(cls, meta):
        options = cls.options_class(
            meta,
            name=None,
            description=None,
            graphql_type=None,
        )
        options.valid_attrs = ['graphql_type', 'name', 'description', 'abstract']
        return options

    def construct_graphql_type(cls, bases):
        if not cls._meta.graphql_type and not cls._meta.abstract:
            cls._meta.graphql_type = GrapheneScalarType(
                graphene_type=cls,
                name=cls._meta.name or cls.__name__,
                description=cls._meta.description,
                # For passing the assertion in GraphQLScalarType
                serialize=lambda: None
            )

    def construct(cls, *args, **kwargs):
        constructed = super(ScalarTypeMeta, cls).construct(*args, **kwargs)
        if isinstance(cls._meta.graphql_type, GrapheneScalarType):
            cls._meta.graphql_type.setup()
        return constructed


class Scalar(six.with_metaclass(ScalarTypeMeta, TypeProxy)):
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
