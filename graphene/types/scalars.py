import six
from graphql import GraphQLScalarType, GraphQLString, GraphQLInt, GraphQLFloat, GraphQLBoolean

from .definitions import ClassTypeMeta, GrapheneScalarType
from .field import Field


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


class Scalar(six.with_metaclass(ScalarTypeMeta)):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def as_field(self):
        return Field(
            lambda: self._meta.graphql_type,
            *self.args,
            **self.kwargs
        )

    def contribute_to_class(self, cls, attname):
        field = self.as_field()
        return field.contribute_to_class(cls, attname)


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
