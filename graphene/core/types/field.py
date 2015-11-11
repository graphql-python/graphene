import six
from collections import OrderedDict
from functools import wraps

from graphql.core.type import GraphQLField, GraphQLInputObjectField

from .base import LazyType, OrderedType
from .argument import to_arguments
from ...utils import to_camel_case
from ..types import BaseObjectType, InputObjectType


class Empty(object):
    pass
 

class Field(OrderedType):
    def __init__(self, type, description=None, args=None, name=None, resolver=None, *args_list, **kwargs):
        _creation_counter = kwargs.pop('_creation_counter', None)
        super(Field, self).__init__(_creation_counter=_creation_counter)
        self.name = name
        if isinstance(type, six.string_types) and type != 'self':
            type = LazyType(type)
        self.type = type
        self.description = description
        args = OrderedDict(args or {}, **kwargs)
        self.arguments = to_arguments(*args_list, **args)
        self.object_type = None
        self.resolver = resolver

    def contribute_to_class(self, cls, attname):
        assert issubclass(cls, BaseObjectType), 'Field {} cannot be mounted in {}'.format(self, cls)
        if not self.name:
            self.name = to_camel_case(attname)
        self.attname = attname
        self.object_type = cls
        if self.type == 'self':
            self.type = cls
        cls._meta.add_field(self)

    @property
    def resolver(self):
        return self._resolver or self.get_resolver_fn()

    @resolver.setter
    def resolver(self, value):
        self._resolver = value

    def get_resolver_fn(self):
        resolve_fn_name = 'resolve_%s' % self.attname
        if hasattr(self.object_type, resolve_fn_name):
            resolve_fn = getattr(self.object_type, resolve_fn_name)

            @wraps(resolve_fn)
            def custom_resolve_fn(instance, args, info):
                return resolve_fn(instance, args, info)
            return custom_resolve_fn
        
        def default_getter(instance, args, info):
             return getattr(instance, self.attname, None)

        return default_getter

    def internal_type(self, schema):
        resolver = self.resolver
        description = self.description
        if not description and resolver:
            description = resolver.__doc__
        type = schema.T(self.type)
        assert type, 'Internal type for field %s is None' % str(self)
        return GraphQLField(type, args=self.get_arguments(schema), resolver=resolver,
                            description=description,)

    def get_arguments(self, schema):
        if not self.arguments:
            return None

        return OrderedDict([(arg.name, schema.T(arg)) for arg in self.arguments])

    def __copy__(self):
        obj = Empty()
        obj.__class__ = self.__class__
        obj.__dict__ = self.__dict__.copy()
        obj.object_type = None
        return obj

    def __repr__(self):
        """
        Displays the module, class and name of the field.
        """
        path = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        name = getattr(self, 'attname', None)
        if name is not None:
            return '<%s: %s>' % (path, name)
        return '<%s>' % path

    def __str__(self):
        """ Return "object_type.field_name". """
        return '%s.%s' % (self.object_type.__name__, self.attname)

    def __hash__(self):
        return hash((self.creation_counter, self.object_type))


class InputField(OrderedType):
    def __init__(self, type, description=None, default=None, name=None, _creation_counter=None):
        super(InputField, self).__init__(_creation_counter=_creation_counter)
        self.name = name
        self.type = type
        self.description = description
        self.default = default

    def contribute_to_class(self, cls, attname):
        assert issubclass(cls, InputObjectType), 'InputField {} cannot be mounted in {}'.format(self, cls)
        if not self.name:
            self.name = to_camel_case(attname)
        self.attname = attname
        self.object_type = cls
        cls._meta.add_field(self)

    def internal_type(self, schema):
        return GraphQLInputObjectField(schema.T(self.type), default_value=self.default,
                                       description=self.description)
