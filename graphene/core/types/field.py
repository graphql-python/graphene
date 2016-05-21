from collections import OrderedDict
from functools import wraps

import six
from graphql.type import GraphQLField, GraphQLInputObjectField

from ...utils import maybe_func
from ...utils.wrap_resolver_function import wrap_resolver_function
from ..classtypes.base import FieldsClassType
from ..classtypes.inputobjecttype import InputObjectType
from ..classtypes.mutation import Mutation
from ..exceptions import SkipField
from .argument import Argument, ArgumentsGroup
from .base import (ArgumentType, GroupNamedType, LazyType, MountType,
                   NamedType, OrderedType)
from .definitions import NonNull


class Field(NamedType, OrderedType):

    def __init__(
            self, type, description=None, args=None, name=None, resolver=None,
            source=None, required=False, default=None, deprecation_reason=None,
            *args_list, **kwargs):
        _creation_counter = kwargs.pop('_creation_counter', None)
        if isinstance(name, (Argument, ArgumentType)):
            kwargs['name'] = name
            name = None
        super(Field, self).__init__(name=name, _creation_counter=_creation_counter)
        if isinstance(type, six.string_types):
            type = LazyType(type)
        self.required = required
        self.type = type
        self.description = description
        self.deprecation_reason = deprecation_reason
        args = OrderedDict(args or {}, **kwargs)
        self.arguments = ArgumentsGroup(*args_list, **args)
        self.object_type = None
        self.attname = None
        self.default_name = None
        self.resolver_fn = resolver
        self.source = source
        assert not (self.source and self.resolver_fn), ('You cannot have a source'
                                                        ' and a resolver at the same time')
        self.default = default

    def contribute_to_class(self, cls, attname):
        assert issubclass(
            cls, (FieldsClassType)), 'Field {} cannot be mounted in {}'.format(
            self, cls)
        self.attname = attname
        self.default_name = attname
        self.object_type = cls
        self.mount(cls)
        if isinstance(self.type, MountType):
            self.type.mount(cls)
        cls._meta.add_field(self)

    @property
    def resolver(self):
        resolver = self.get_resolver_fn()
        return resolver

    @property
    def default(self):
        if callable(self._default):
            return self._default()
        return self._default

    @default.setter
    def default(self, value):
        self._default = value

    def get_resolver_fn(self):
        if self.resolver_fn:
            return self.resolver_fn

        resolve_fn_name = 'resolve_%s' % self.attname
        if hasattr(self.object_type, resolve_fn_name):
            return getattr(self.object_type, resolve_fn_name)

        def default_getter(instance, args, info):
            value = getattr(instance, self.source or self.attname, self.default)
            return maybe_func(value)
        return default_getter

    def get_type(self, schema):
        if self.required:
            return NonNull(self.type)
        return self.type

    def internal_type(self, schema):
        if not self.object_type:
            raise Exception('The field is not mounted in any ClassType')
        resolver = self.resolver
        description = self.description
        arguments = self.arguments
        if not description and resolver:
            description = resolver.__doc__
        type = schema.T(self.get_type(schema))
        type_objecttype = schema.objecttype(type)
        if type_objecttype and issubclass(type_objecttype, Mutation):
            assert len(arguments) == 0
            arguments = type_objecttype.get_arguments()
            resolver = getattr(type_objecttype, 'mutate')
            resolver = wrap_resolver_function(resolver)
        else:
            my_resolver = wrap_resolver_function(resolver)

            @wraps(my_resolver)
            def wrapped_func(instance, args, context, info):
                if not isinstance(instance, self.object_type):
                    instance = self.object_type(_root=instance)
                return my_resolver(instance, args, context, info)
            resolver = wrapped_func

        assert type, 'Internal type for field %s is None' % str(self)
        return GraphQLField(
            type,
            args=schema.T(arguments),
            resolver=schema.resolver_with_middleware(resolver),
            deprecation_reason=self.deprecation_reason,
            description=description,
        )

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

    def __eq__(self, other):
        eq = super(Field, self).__eq__(other)
        if isinstance(self, type(other)):
            return eq and self.object_type == other.object_type
        return NotImplemented

    def __hash__(self):
        return hash((self.creation_counter, self.object_type))


class InputField(NamedType, OrderedType):

    def __init__(self, type, description=None, default=None,
                 name=None, _creation_counter=None, required=False):
        super(InputField, self).__init__(_creation_counter=_creation_counter)
        if isinstance(type, six.string_types):
            type = LazyType(type)
        if required:
            type = NonNull(type)
        self.type = type
        self.description = description
        self.default = default

    def contribute_to_class(self, cls, attname):
        assert issubclass(
            cls, (InputObjectType)), 'InputField {} cannot be mounted in {}'.format(
            self, cls)
        self.attname = attname
        self.default_name = attname
        self.object_type = cls
        self.mount(cls)
        if isinstance(self.type, MountType):
            self.type.mount(cls)
        cls._meta.add_field(self)

    def internal_type(self, schema):
        return GraphQLInputObjectField(
            schema.T(self.type),
            default_value=self.default, description=self.description
        )


class FieldsGroupType(GroupNamedType):

    def iter_types(self, schema):
        for field in sorted(self.types):
            try:
                yield self.get_named_type(schema, field)
            except SkipField:
                continue
