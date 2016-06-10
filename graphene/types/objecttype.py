import copy
import six

from graphql import GraphQLObjectType

from .definitions import FieldsMeta, ClassTypeMeta, GrapheneGraphQLType
from .interface import GrapheneInterfaceType


class GrapheneObjectType(GrapheneGraphQLType, GraphQLObjectType):

    def __init__(self, *args, **kwargs):
        super(GrapheneObjectType, self).__init__(*args, **kwargs)
        self.check_interfaces()

    def check_interfaces(self):
        if not self._provided_interfaces:
            return
        for interface in self._provided_interfaces:
            if isinstance(interface, GrapheneInterfaceType):
                interface.graphene_type.implements(self.graphene_type)

    @property
    def is_type_of(self):
        return self._is_type_of or self.default_is_type_of

    @is_type_of.setter
    def is_type_of(self, is_type_of):
        self._is_type_of = is_type_of

    def default_is_type_of(self, interface, context, info):
        from ..utils.get_graphql_type import get_graphql_type
        try:
            graphql_type = get_graphql_type(type(interface))
            return graphql_type.name == self.name
        except:
            return False


def get_interfaces(cls, interfaces):
    from ..utils.get_graphql_type import get_graphql_type

    for interface in interfaces:
        graphql_type = get_graphql_type(interface)
        yield graphql_type


class ObjectTypeMeta(FieldsMeta, ClassTypeMeta):

    def get_options(cls, meta):
        return cls.options_class(
            meta,
            name=None,
            description=None,
            graphql_type=None,
            interfaces=[],
            abstract=False
        )

    def construct(cls, bases, attrs):
        if not cls._meta.abstract:
            interfaces = tuple(get_interfaces(cls, cls._meta.interfaces))
            local_fields = cls._extract_local_fields(attrs)
            if not cls._meta.graphql_type:
                cls = super(ObjectTypeMeta, cls).construct(bases, attrs)
                cls._meta.graphql_type = GrapheneObjectType(
                    graphene_type=cls,
                    name=cls._meta.name or cls.__name__,
                    description=cls._meta.description or cls.__doc__,
                    fields=cls._fields(bases, attrs, local_fields, interfaces),
                    interfaces=interfaces,
                )
                return cls
            else:
                assert not local_fields, "Can't mount Fields in an ObjectType with a defined graphql_type"

        return super(ObjectTypeMeta, cls).construct(bases, attrs)


def implements(*interfaces):
    # This function let us decorate a ObjectType
    # Adding a specified interfaces into the graphql_type
    def wrap_class(cls):
        interface_types = get_interfaces(cls, interfaces)
        graphql_type = cls._meta.graphql_type
        # fields = cls._build_field_map(interface_types, graphql_type.get_fields().values())
        new_type = copy.copy(graphql_type)
        new_type._provided_interfaces = tuple(graphql_type._provided_interfaces) + tuple(interface_types)
        new_type._fields = graphql_type._fields
        cls._meta.graphql_type = new_type
        cls._meta.graphql_type.check_interfaces()
        return cls
    return wrap_class


class ObjectType(six.with_metaclass(ObjectTypeMeta)):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        # GraphQL ObjectType acting as container
        args_len = len(args)
        fields = self._meta.graphql_type.get_fields().values()
        if args_len > len(fields):
            # Daft, but matches old exception sans the err msg.
            raise IndexError("Number of args exceeds number of fields")
        fields_iter = iter(fields)

        if not kwargs:
            for val, field in zip(args, fields_iter):
                attname = getattr(field, 'attname', field.name)
                setattr(self, attname, val)
        else:
            for val, field in zip(args, fields_iter):
                attname = getattr(field, 'attname', field.name)
                setattr(self, attname, val)
                kwargs.pop(attname, None)

        for field in fields_iter:
            try:
                attname = getattr(field, 'attname', field.name)
                val = kwargs.pop(attname)
                setattr(self, attname, val)
            except KeyError:
                pass

        if kwargs:
            for prop in list(kwargs):
                try:
                    if isinstance(getattr(self.__class__, prop), property):
                        setattr(self, prop, kwargs.pop(prop))
                except AttributeError:
                    pass
            if kwargs:
                raise TypeError(
                    "'%s' is an invalid keyword argument for this function" %
                    list(kwargs)[0])
