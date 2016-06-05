import six

from graphql import GraphQLObjectType

from .definitions import ClassTypeMeta, GrapheneFieldsType, FieldMap
from .interface import GrapheneInterfaceType


class GrapheneObjectType(GrapheneFieldsType, GraphQLObjectType):

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
            return graphql_type == self
        except:
            return False

    def add_interface(self, interface):
        from ..utils.get_graphql_type import get_graphql_type
        # We clear the cached interfaces
        self._interfaces = None
        # We clear the cached fields as could be inherited from interfaces
        self._field_map = None
        graphql_type = get_graphql_type(interface)

        if isinstance(graphql_type, GrapheneInterfaceType):
            graphql_type.graphene_type.implements(self.graphene_type)

        self._provided_interfaces.append(graphql_type)


class ObjectTypeMeta(ClassTypeMeta):

    def get_options(cls, meta):
        options = cls.options_class(
            meta,
            name=None,
            description=None,
            graphql_type=None,
            interfaces=[],
        )
        options.valid_attrs = ['graphql_type', 'name', 'description', 'interfaces', 'abstract']
        return options

    def construct_graphql_type(cls, bases):
        if not cls._meta.graphql_type and not cls._meta.abstract:
            from ..utils.get_graphql_type import get_graphql_type
            from ..utils.is_graphene_type import is_graphene_type
            inherited_types = [
                base._meta.graphql_type for base in bases if is_graphene_type(base)
            ]

            cls._meta.graphql_type = GrapheneObjectType(
                graphene_type=cls,
                name=cls._meta.name or cls.__name__,
                description=cls._meta.description,
                fields=FieldMap(cls, bases=filter(None, inherited_types)),
                interfaces=[],
            )
            for interface in cls._meta.interfaces:
                cls._meta.graphql_type.add_interface(interface)


def implements(*interfaces):
    # This function let us decorate a ObjectType
    # Adding a specified interfaces into the graphql_type
    def wrap_class(cls):

        for i in interfaces:
            cls._meta.graphql_type.add_interface(i)
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
