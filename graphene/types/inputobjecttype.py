import six

from graphql import GraphQLInputObjectType

from .definitions import GrapheneGraphQLType
from .interface import attrs_without_fields
from .unmountedtype import UnmountedType
from .options import Options
from ..utils.is_base_type import is_base_type
from ..utils.get_fields import get_fields
from ..utils.copy_fields import copy_fields
from .field import InputField


class GrapheneInputObjectType(GrapheneGraphQLType, GraphQLInputObjectType):
    pass


class InputObjectTypeMeta(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(InputObjectTypeMeta, cls).__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, InputObjectTypeMeta):
            return super_new(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=None,
            description=None,
            graphql_type=None,
            abstract=False
        )

        fields = get_fields(InputObjectType, attrs, bases)
        attrs = attrs_without_fields(attrs, fields)
        cls = super_new(cls, name, bases, dict(attrs, _meta=options))

        if not options.graphql_type:
            fields = copy_fields(InputField, fields, parent=cls)
            options.graphql_type = GrapheneInputObjectType(
                graphene_type=cls,
                name=options.name or cls.__name__,
                description=options.description or cls.__doc__,
                fields=fields,
            )
        else:
            assert not fields, "Can't mount InputFields in an InputObjectType with a defined graphql_type"
            fields = copy_fields(InputField, options.graphql_type.get_fields(), parent=cls)

        for name, field in fields.items():
            setattr(cls, field.attname or name, field)

        return cls


class InputObjectType(six.with_metaclass(InputObjectTypeMeta, UnmountedType)):
    pass
