
import six

from ..utils.copy_fields import copy_fields
from ..utils.get_fields import get_fields
from ..utils.is_base_type import is_base_type
from .field import Field
from .options import Options


from ..generators import generate_interface, generate_objecttype


def get_interfaces(interfaces):
    from ..utils.get_graphql_type import get_graphql_type

    for interface in interfaces:
        graphql_type = get_graphql_type(interface)
        yield graphql_type


def is_objecttype(bases):
    for base in bases:
        if issubclass(base, ObjectType):
            return True
    return False


def attrs_without_fields(attrs, fields):
    return {k: v for k, v in attrs.items() if k not in fields}


# We inherit from InterfaceTypeMeta instead of type for being able
# to have ObjectTypes extending Interfaces using Python syntax, like:
# class MyObjectType(ObjectType, MyInterface)
class ObjectTypeMeta(type):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # ObjectType,or Interfaces
        if not is_base_type(bases, ObjectTypeMeta):
            return type.__new__(cls, name, bases, attrs)

        if not is_objecttype(bases):
            return cls._create_interface(cls, name, bases, attrs)

        return cls._create_objecttype(cls, name, bases, attrs)

    def get_interfaces(cls, bases):  # noqa: N805
        return (b for b in bases if issubclass(b, Interface))

    def is_object_type(cls):  # noqa: N805
        return issubclass(cls, ObjectType)

    @staticmethod
    def _get_interface_options(meta):
        return Options(
            meta,
            name=None,
            description=None,
            graphql_type=None,
        )

    @staticmethod
    def _create_interface(cls, name, bases, attrs):
        options = cls._get_interface_options(attrs.pop('Meta', None))

        fields = get_fields(Interface, attrs, bases)
        attrs = attrs_without_fields(attrs, fields)
        cls = type.__new__(cls, name, bases, dict(attrs, _meta=options))

        if not options.graphql_type:
            fields = copy_fields(Field, fields, parent=cls)
            options.get_fields = lambda: fields
            options.graphql_type = generate_interface(cls)
        else:
            assert not fields, "Can't mount Fields in an Interface with a defined graphql_type"
            fields = copy_fields(Field, options.graphql_type.get_fields(), parent=cls)
            options.get_fields = lambda: fields

        for name, field in fields.items():
            setattr(cls, field.attname or name, field)

        return cls

    @staticmethod
    def _create_objecttype(cls, name, bases, attrs):
        options = Options(
            attrs.pop('Meta', None),
            name=None,
            description=None,
            graphql_type=None,
            interfaces=(),
        )

        interfaces = tuple(options.interfaces)
        fields = get_fields(ObjectType, attrs, bases, interfaces)
        attrs = attrs_without_fields(attrs, fields)
        cls = type.__new__(cls, name, bases, dict(attrs, _meta=options))

        if not options.graphql_type:
            fields = copy_fields(Field, fields, parent=cls)
            base_interfaces = tuple(b for b in bases if issubclass(b, Interface))
            options.get_fields = lambda: fields
            options.get_interfaces = tuple(get_interfaces(interfaces + base_interfaces))
            options.graphql_type = generate_objecttype(cls)
        else:
            assert not fields, "Can't mount Fields in an ObjectType with a defined graphql_type"
            fields = copy_fields(Field, options.graphql_type.get_fields(), parent=cls)

            options.get_fields = lambda: fields

        for name, field in fields.items():
            setattr(cls, field.attname or name, field)

        return cls


class ObjectType(six.with_metaclass(ObjectTypeMeta)):

    def __init__(self, *args, **kwargs):
        # GraphQL ObjectType acting as container
        args_len = len(args)
        fields = self._meta.get_fields().items()
        for name, f in fields:
            setattr(self, getattr(f, 'attname', name), None)

        if args_len > len(fields):
            # Daft, but matches old exception sans the err msg.
            raise IndexError("Number of args exceeds number of fields")
        fields_iter = iter(fields)

        if not kwargs:
            for val, (name, field) in zip(args, fields_iter):
                attname = getattr(field, 'attname', name)
                setattr(self, attname, val)
        else:
            for val, (name, field) in zip(args, fields_iter):
                attname = getattr(field, 'attname', name)
                setattr(self, attname, val)
                kwargs.pop(attname, None)

        for name, field in fields_iter:
            try:
                attname = getattr(field, 'attname', name)
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

    @classmethod
    def is_type_of(cls, interface, context, info):
        from ..utils.get_graphql_type import get_graphql_type
        try:
            graphql_type = get_graphql_type(type(interface))
            return graphql_type.name == cls._meta.graphql_type.name
        except:
            return False


class Interface(six.with_metaclass(ObjectTypeMeta)):
    resolve_type = None

    def __init__(self, *args, **kwargs):
        from .objecttype import ObjectType
        if not isinstance(self, ObjectType):
            raise Exception("An interface cannot be intitialized")
        super(Interface, self).__init__(*args, **kwargs)
