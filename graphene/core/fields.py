import inspect
import six
from functools import total_ordering
from graphql.core.type import (
    GraphQLField,
    GraphQLList,
    GraphQLNonNull,
    GraphQLInt,
    GraphQLString,
    GraphQLBoolean,
    GraphQLID,
    GraphQLArgument,
    GraphQLFloat,
)
from graphene.utils import memoize, to_camel_case
from graphene.core.types import BaseObjectType
from graphene.core.scalars import GraphQLSkipField


@total_ordering
class Field(object):
    SKIP = GraphQLSkipField
    creation_counter = 0

    def __init__(self, field_type, name=None, resolve=None, required=False, args=None, description='', **extra_args):
        self.field_type = field_type
        self.resolve_fn = resolve
        self.required = required
        self.args = args or {}
        self.extra_args = extra_args
        self._type = None
        self.name = name
        self.description = description or self.__doc__
        self.object_type = None
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def contribute_to_class(self, cls, name):
        if not self.name:
            self.name = to_camel_case(name)
        self.field_name = name
        self.object_type = cls
        if isinstance(self.field_type, Field) and not self.field_type.object_type:
            self.field_type.contribute_to_class(cls, name)
        cls._meta.add_field(self)

    def resolve(self, instance, args, info):
        if self.resolve_fn:
            resolve_fn = self.resolve_fn
        else:
            resolve_fn = lambda root, args, info: root.resolve(
                self.field_name, args, info)
        return resolve_fn(instance, args, info)

    def get_object_type(self, schema):
        field_type = self.field_type
        _is_class = inspect.isclass(field_type)
        if isinstance(field_type, Field):
            return field_type.get_object_type(schema)
        if _is_class and issubclass(field_type, BaseObjectType):
            return field_type
        elif isinstance(field_type, six.string_types):
            if field_type == 'self':
                return self.object_type
            else:
                return schema.get_type(field_type)

    def type_wrapper(self, field_type):
        if self.required:
            field_type = GraphQLNonNull(field_type)
        return field_type

    @memoize
    def internal_type(self, schema):
        field_type = self.field_type
        if isinstance(field_type, Field):
            field_type = self.field_type.internal_type(schema)
        else:
            object_type = self.get_object_type(schema)
            if object_type:
                field_type = object_type.internal_type(schema)

        field_type = self.type_wrapper(field_type)
        return field_type

    @memoize
    def internal_field(self, schema):
        if not self.object_type:
            raise Exception(
                'Field could not be constructed in a non graphene.Type or graphene.Interface')

        extra_args = self.extra_args.copy()
        for arg_name, arg_value in self.extra_args.items():
            if isinstance(arg_value, GraphQLArgument):
                self.args[arg_name] = arg_value
                del extra_args[arg_name]

        if extra_args != {}:
            raise TypeError("Field %s.%s initiated with invalid args: %s" % (
                self.object_type,
                self.field_name,
                ','.join(extra_args.keys())
            ))

        internal_type = self.internal_type(schema)
        if not internal_type:
            raise Exception("Internal type for field %s is None" % self)

        return GraphQLField(
            internal_type,
            description=self.description,
            args=self.args,
            resolver=self.resolve,
        )

    def __str__(self):
        """ Return "object_type.name". """
        return '%s.%s' % (self.object_type, self.field_name)

    def __repr__(self):
        """
        Displays the module, class and name of the field.
        """
        path = '%s.%s' % (self.__class__.__module__, self.__class__.__name__)
        name = getattr(self, 'field_name', None)
        if name is not None:
            return '<%s: %s>' % (path, name)
        return '<%s>' % path

    def __eq__(self, other):
        # Needed for @total_ordering
        if isinstance(other, Field):
            return self.creation_counter == other.creation_counter
        return NotImplemented

    def __lt__(self, other):
        # This is needed because bisect does not take a comparison function.
        if isinstance(other, Field):
            return self.creation_counter < other.creation_counter
        return NotImplemented

    def __hash__(self):
        return hash(self.creation_counter)


class NativeField(Field):

    def __init__(self, field=None):
        super(NativeField, self).__init__(None)
        self.field = field

    def get_field(self, schema):
        return self.field

    @memoize
    def internal_field(self, schema):
        return self.get_field(schema)

    @memoize
    def internal_type(self, schema):
        return self.internal_field(schema).type


class LazyField(Field):

    @memoize
    def inner_field(self, schema):
        return self.get_field(schema)

    def internal_type(self, schema):
        return self.inner_field(schema).internal_type(schema)

    def internal_field(self, schema):
        return self.inner_field(schema).internal_field(schema)


class LazyNativeField(NativeField):

    def __init__(self, *args, **kwargs):
        super(LazyNativeField, self).__init__(None, *args, **kwargs)

    def get_field(self, schema):
        raise NotImplementedError(
            "get_field function not implemented for %s LazyField" % self.__class__)

    @memoize
    def internal_field(self, schema):
        return self.get_field(schema)

    @memoize
    def internal_type(self, schema):
        return self.internal_field(schema).type


class TypeField(Field):

    def __init__(self, *args, **kwargs):
        super(TypeField, self).__init__(self.field_type, *args, **kwargs)


class StringField(TypeField):
    field_type = GraphQLString


class IntField(TypeField):
    field_type = GraphQLInt


class BooleanField(TypeField):
    field_type = GraphQLBoolean


class IDField(TypeField):
    field_type = GraphQLID


class FloatField(TypeField):
    field_type = GraphQLFloat


class ListField(Field):
    def type_wrapper(self, field_type):
        return GraphQLList(field_type)


class NonNullField(Field):
    def type_wrapper(self, field_type):
        return GraphQLNonNull(field_type)
