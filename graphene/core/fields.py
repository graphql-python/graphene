import inspect
import six
from functools import total_ordering, wraps
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
    GraphQLInputObjectField,
)
from graphene.utils import to_camel_case
from graphene.core.types import BaseObjectType, InputObjectType
from graphene.core.scalars import GraphQLSkipField


class Empty(object):
    pass


@total_ordering
class Field(object):
    SKIP = GraphQLSkipField
    creation_counter = 0
    required = False

    def __init__(self, field_type, name=None, resolve=None, required=False, args=None, description='', default=None, **extra_args):
        self.field_type = field_type
        self.resolve_fn = resolve
        self.required = self.required or required
        self.args = args or {}
        self.extra_args = extra_args
        self._type = None
        self.name = name
        self.description = description or self.__doc__
        self.object_type = None
        self.default = default
        self.creation_counter = Field.creation_counter
        Field.creation_counter += 1

    def get_default(self):
        return self.default

    def contribute_to_class(self, cls, name, add=True):
        if not self.name:
            self.name = to_camel_case(name)
        self.field_name = name
        self.object_type = cls
        if isinstance(self.field_type, Field) and not self.field_type.object_type:
            self.field_type.contribute_to_class(cls, name, False)
        if add:
            cls._meta.add_field(self)

    def resolve(self, instance, args, info):
        schema = info and getattr(info.schema, 'graphene_schema', None)
        resolve_fn = self.get_resolve_fn(schema)
        if resolve_fn:
            return resolve_fn(instance, args, info)
        else:
            return getattr(instance, self.field_name, self.get_default())

    def get_resolve_fn(self, schema):
        object_type = self.get_object_type(schema)
        if object_type and object_type._meta.is_mutation:
            return object_type.mutate
        elif self.resolve_fn:
            return self.resolve_fn
        else:
            custom_resolve_fn_name = 'resolve_%s' % self.field_name
            if hasattr(self.object_type, custom_resolve_fn_name):
                resolve_fn = getattr(self.object_type, custom_resolve_fn_name)

                @wraps(resolve_fn)
                def custom_resolve_fn(instance, args, info):
                    return resolve_fn(instance, args, info)
                return custom_resolve_fn

    def get_object_type(self, schema):
        field_type = self.field_type
        if inspect.isfunction(field_type):
            field_type = field_type(self)
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

    def internal_field(self, schema):
        if not self.object_type:
            raise Exception(
                'Field could not be constructed in a non graphene.ObjectType or graphene.Interface')

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

        args = self.args

        object_type = self.get_object_type(schema)
        if object_type and object_type._meta.is_mutation:
            assert not self.args, 'Arguments provided for mutations are defined in Input class in Mutation'
            args = object_type.get_input_type().fields_as_arguments(schema)

        internal_type = self.internal_type(schema)
        if not internal_type:
            raise Exception("Internal type for field %s is None" % self)

        description = self.description
        resolve_fn = self.get_resolve_fn(schema)
        if resolve_fn:
            description = resolve_fn.__doc__ or description

            @wraps(resolve_fn)
            def resolver(*args):
                return self.resolve(*args)
        else:
            resolver = self.resolve

        if issubclass(self.object_type, InputObjectType):
            return GraphQLInputObjectField(
                internal_type,
                description=description,
            )

        return GraphQLField(
            internal_type,
            description=description,
            args=args,
            resolver=resolver,
        )

    def __str__(self):
        """ Return "object_type.name". """
        return '%s.%s' % (self.object_type.__name__, self.field_name)

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
            return self.creation_counter == other.creation_counter and \
                self.object_type == other.object_type
        return NotImplemented

    def __lt__(self, other):
        # This is needed because bisect does not take a comparison function.
        if isinstance(other, Field):
            return self.creation_counter < other.creation_counter
        return NotImplemented

    def __hash__(self):
        return hash((self.creation_counter, self.object_type))

    def __copy__(self):
        # We need to avoid hitting __reduce__, so define this
        # slightly weird copy construct.
        obj = Empty()
        obj.__class__ = self.__class__
        obj.__dict__ = self.__dict__.copy()
        if self.field_type == 'self':
            obj.field_type = self.object_type
        return obj


class LazyField(Field):

    def inner_field(self, schema):
        return self.get_field(schema)

    def internal_type(self, schema):
        return self.inner_field(schema).internal_type(schema)

    def internal_field(self, schema):
        return self.inner_field(schema).internal_field(schema)


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
