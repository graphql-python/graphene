import six

from graphql import GraphQLInterfaceType
from .definitions import FieldsMeta, ClassTypeMeta, GrapheneGraphQLType
from .options import Options
from ..utils.is_base_type import is_base_type

class GrapheneInterfaceType(GrapheneGraphQLType, GraphQLInterfaceType):
    pass


class InterfaceTypeMeta(type):

    def __new__(cls, name, bases, attrs):
        super_new = super(InterfaceTypeMeta, cls).__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, InterfaceTypeMeta):
            return super_new(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=None,
            description=None,
            graphql_type=None,
            abstract=False
        )

        from ..utils.get_fields import get_fields

        fields = get_fields(Interface, attrs, bases)
        attrs = attrs_without_fields(attrs, fields)
        cls = super_new(cls, name, bases, dict(attrs, _meta=options))

        if not options.graphql_type:
            fields = copy_fields(fields)
            options.graphql_type = GrapheneInterfaceType(
                graphene_type=cls,
                name=options.name or cls.__name__,
                description=options.description or cls.__doc__,
                fields=fields,
            )
        else:
            assert not fields, "Can't mount Fields in an Interface with a defined graphql_type"
            fields = copy_fields(options.graphql_type.get_fields())

        for attname, field in fields.items():
            field.parent = cls
            # setattr(cls, field.name, field)

        return cls


def attrs_without_fields(attrs, fields):
    fields_names = fields.keys()
    return {k: v for k, v in attrs.items() if k not in fields_names}


def copy_fields(fields):
    from collections import OrderedDict
    from .field import Field

    _fields = []
    for attname, field in fields.items():
        field = Field.copy_and_extend(field, attname=attname)
        _fields.append(field)

    return OrderedDict((f.name, f) for f in sorted(_fields))


class Interface(six.with_metaclass(InterfaceTypeMeta)):

    def __init__(self, *args, **kwargs):
        from .objecttype import ObjectType
        if not isinstance(self, ObjectType):
            raise Exception("An interface cannot be intitialized")
        super(Interface, self).__init__(*args, **kwargs)

    @classmethod
    def implements(cls, object_type):
        '''
        We use this function for customizing when a ObjectType have this class as Interface
        For example, if we want to check that the ObjectType have some required things
        in it like Node.get_node
        '''
        pass
