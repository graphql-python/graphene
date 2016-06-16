import copy

import six

from graphql import GraphQLObjectType

from ..utils.copy_fields import copy_fields
from ..utils.get_fields import get_fields
from ..utils.is_base_type import is_base_type
from .definitions import GrapheneGraphQLType
from .field import Field
from .interface import (GrapheneInterfaceType, Interface, InterfaceTypeMeta,
                        attrs_without_fields)
from .options import Options


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


def get_interfaces(interfaces):
    from ..utils.get_graphql_type import get_graphql_type

    for interface in interfaces:
        graphql_type = get_graphql_type(interface)
        yield graphql_type


# We inherit from InterfaceTypeMeta instead of type for being able
# to have ObjectTypes extending Interfaces using Python syntax, like:
# class MyObjectType(ObjectType, MyInterface)
class ObjectTypeMeta(InterfaceTypeMeta):

    def __new__(cls, name, bases, attrs):
        super_new = type.__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, ObjectTypeMeta):
            return super_new(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=None,
            description=None,
            graphql_type=None,
            interfaces=(),
            abstract=False
        )

        interfaces = tuple(options.interfaces)
        fields = get_fields(ObjectType, attrs, bases, interfaces)
        attrs = attrs_without_fields(attrs, fields)
        cls = super_new(cls, name, bases, dict(attrs, _meta=options))

        if not options.graphql_type:
            fields = copy_fields(Field, fields, parent=cls)
            base_interfaces = tuple(b for b in bases if issubclass(b, Interface))
            options.graphql_type = GrapheneObjectType(
                graphene_type=cls,
                name=options.name or cls.__name__,
                description=options.description or cls.__doc__,
                fields=fields,
                interfaces=tuple(get_interfaces(interfaces + base_interfaces))
            )
        else:
            assert not fields, "Can't mount Fields in an ObjectType with a defined graphql_type"
            fields = copy_fields(Field, options.graphql_type.get_fields(), parent=cls)

        for name, field in fields.items():
            setattr(cls, field.attname or name, field)

        return cls

    def get_interfaces(cls, bases):
        return (b for b in bases if issubclass(b, Interface))

    def is_object_type(cls):
        return issubclass(cls, ObjectType)


class ObjectType(six.with_metaclass(ObjectTypeMeta)):

    def __init__(self, *args, **kwargs):
        # GraphQL ObjectType acting as container
        args_len = len(args)
        fields = self._meta.graphql_type.get_fields().values()
        for f in fields:
            setattr(self, getattr(f, 'attname', f.name), None)

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
