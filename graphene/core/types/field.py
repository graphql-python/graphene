import six
from collections import OrderedDict
from functools import wraps

from graphql.core.type import GraphQLField, GraphQLInputObjectField

from .base import MountType, LazyType, OrderedType
from .argument import ArgumentsGroup
from .definitions import NonNull
from ...utils import to_camel_case, ProxySnakeDict
from ..types import BaseObjectType, InputObjectType


def make_args_snake_case(resolver):
    @wraps(resolver)
    def wrapped_resolver(instance, args, info):
        return resolver(instance, ProxySnakeDict(args), info)

    return wrapped_resolver


class Empty(object):
    pass


class Field(OrderedType):
    def __init__(self, type, description=None, args=None, name=None, resolver=None, required=False, default=None, *args_list, **kwargs):
        _creation_counter = kwargs.pop('_creation_counter', None)
        super(Field, self).__init__(_creation_counter=_creation_counter)
        self.name = name
        if isinstance(type, six.string_types):
            type = LazyType(type)
        self.required = required
        if self.required:
            type = NonNull(type)
        self.type = type
        self.description = description
        args = OrderedDict(args or {}, **kwargs)
        self.arguments = ArgumentsGroup(*args_list, **args)
        self.object_type = None
        self.resolver = resolver
        self.default = default

    def contribute_to_class(self, cls, attname):
        assert issubclass(cls, BaseObjectType), 'Field {} cannot be mounted in {}'.format(self, cls)
        if not self.name:
            self.name = to_camel_case(attname)
        self.attname = attname
        self.object_type = cls
        self.mount(cls)
        if isinstance(self.type, MountType):
            self.type.mount(cls)
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
            return getattr(self.object_type, resolve_fn_name)

        def default_getter(instance, args, info):
            return getattr(instance, self.attname, self.default)
        return default_getter

    def get_type(self, schema):
        return self.type

    def internal_type(self, schema):
        resolver = self.resolver
        description = self.description
        arguments = self.arguments
        if not description and resolver:
            description = resolver.__doc__
        type = schema.T(self.get_type(schema))
        type_objecttype = schema.objecttype(type)
        if type_objecttype and type_objecttype._meta.is_mutation:
            assert len(arguments) == 0
            arguments = type_objecttype.get_arguments()
            resolver = getattr(type_objecttype, 'mutate')

        resolver = make_args_snake_case(resolver)
        assert type, 'Internal type for field %s is None' % str(self)
        return GraphQLField(type, args=schema.T(arguments), resolver=resolver,
                            description=description,)

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
    def __init__(self, type, description=None, default=None, name=None, _creation_counter=None, required=False):
        super(InputField, self).__init__(_creation_counter=_creation_counter)
        self.name = name
        if required:
            type = NonNull(type)
        self.type = type
        self.description = description
        self.default = default

    def contribute_to_class(self, cls, attname):
        assert issubclass(cls, InputObjectType), 'InputField {} cannot be mounted in {}'.format(self, cls)
        if not self.name:
            self.name = to_camel_case(attname)
        self.attname = attname
        self.object_type = cls
        self.mount(cls)
        if isinstance(self.type, MountType):
            self.type.mount(cls)
        cls._meta.add_field(self)

    def internal_type(self, schema):
        return GraphQLInputObjectField(schema.T(self.type), default_value=self.default,
                                       description=self.description)
