from collections import OrderedDict
from functools import wraps

import six
from graphql.core.type import GraphQLField, GraphQLInputObjectField

from ...utils import to_camel_case
from ..classtypes.base import FieldsClassType
from ..classtypes.inputobjecttype import InputObjectType
from ..classtypes.mutation import Mutation
from ..exceptions import SkipField
from .argument import ArgumentsGroup, snake_case_args
from .base import LazyType, NamedType, MountType, OrderedType, GroupNamedType
from .definitions import NonNull


class Field(NamedType, OrderedType):

    def __init__(
            self, type, description=None, args=None, name=None, resolver=None,
            required=False, default=None, *args_list, **kwargs):
        _creation_counter = kwargs.pop('_creation_counter', None)
        super(Field, self).__init__(_creation_counter=_creation_counter)
        self.name = name
        if isinstance(type, six.string_types):
            type = LazyType(type)
        self.required = required
        self.type = type
        self.description = description
        args = OrderedDict(args or {}, **kwargs)
        self.arguments = ArgumentsGroup(*args_list, **args)
        self.object_type = None
        self.resolver_fn = resolver
        self.default = default

    def contribute_to_class(self, cls, attname):
        assert issubclass(
            cls, (FieldsClassType)), 'Field {} cannot be mounted in {}'.format(
            self, cls)
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
        return self.resolver_fn or self.get_resolver_fn()

    def get_resolver_fn(self):
        resolve_fn_name = 'resolve_%s' % self.attname
        if hasattr(self.object_type, resolve_fn_name):
            return getattr(self.object_type, resolve_fn_name)

        def default_getter(instance, args, info):
            return getattr(instance, self.attname, self.default)
        return default_getter

    def get_type(self, schema):
        if self.required:
            return NonNull(self.type)
        return self.type

    def decorate_resolver(self, resolver):
        return snake_case_args(resolver)

    def internal_type(self, schema):
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
        else:
            my_resolver = resolver

            @wraps(my_resolver)
            def wrapped_func(instance, args, info):
                if not isinstance(instance, self.object_type):
                    instance = self.object_type(_root=instance)
                return my_resolver(instance, args, info)
            resolver = wrapped_func

        assert type, 'Internal type for field %s is None' % str(self)
        return GraphQLField(type, args=schema.T(arguments),
                            resolver=self.decorate_resolver(resolver),
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
        self.name = name
        if required:
            type = NonNull(type)
        self.type = type
        self.description = description
        self.default = default

    def contribute_to_class(self, cls, attname):
        assert issubclass(
            cls, (InputObjectType)), 'InputField {} cannot be mounted in {}'.format(
            self, cls)
        if not self.name:
            self.name = to_camel_case(attname)
        self.attname = attname
        self.object_type = cls
        self.mount(cls)
        if isinstance(self.type, MountType):
            self.type.mount(cls)
        cls._meta.add_field(self)

    def internal_type(self, schema):
        return GraphQLInputObjectField(
            schema.T(self.type),
            default_value=self.default, description=self.description)


class FieldsGroupType(GroupNamedType):
    def internal_type(self, schema):
        fields = []
        for field in sorted(self.types):
            try:
                fields.append(self.get_named_type(schema, field))
            except SkipField:
                continue
        return OrderedDict(fields)
