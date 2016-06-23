import six

from graphql import (GraphQLBoolean, GraphQLFloat, GraphQLID, GraphQLInt,
                     GraphQLString)

from ..utils.is_base_type import is_base_type
from .options import Options
from .unmountedtype import UnmountedType

from ..generators import generate_scalar


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
            options.graphql_type = generate_scalar(cls)

        return cls


class Scalar(six.with_metaclass(ScalarTypeMeta, UnmountedType)):
    pass


def construct_scalar_class(graphql_type):
    # This is equivalent to
    # class String(Scalar):
    #     class Meta:
    #         graphql_type = graphql_type
    Meta = type('Meta', (object,), {'graphql_type': graphql_type})
    return type(graphql_type.name, (Scalar, ), {'Meta': Meta})


String = construct_scalar_class(GraphQLString)
Int = construct_scalar_class(GraphQLInt)
Float = construct_scalar_class(GraphQLFloat)
Boolean = construct_scalar_class(GraphQLBoolean)
ID = construct_scalar_class(GraphQLID)
