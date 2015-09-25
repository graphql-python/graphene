from graphql.core.type import (
    GraphQLField,
    GraphQLList,
    GraphQLNonNull,
    GraphQLInt,
    GraphQLString,
    GraphQLBoolean,
    GraphQLID,
    GraphQLArgument,
)
from graphene.utils import cached_property
from graphene.core.utils import get_object_type

class Field(object):
    def __init__(self, field_type, resolve=None, null=True, args=None, description='', **extra_args):
        self.field_type = field_type
        self.resolve_fn = resolve
        self.null = null
        self.args = args or {}
        self.extra_args = extra_args
        self._type = None
        self.description = description or self.__doc__
        self.object_type = None

    def contribute_to_class(self, cls, name):
        self.field_name = name
        self.object_type = cls
        if isinstance(self.field_type, Field) and not self.field_type.object_type:
            self.field_type.contribute_to_class(cls, name)
        cls._meta.add_field(self)

    def resolver(self, instance, args, info):
        if self.object_type.can_resolve(self.field_name, instance, args, info):
            return self.resolve(instance, args, info)
        else:
            return None

    def resolve(self, instance, args, info):
        if self.resolve_fn:
            resolve_fn = self.resolve_fn
        else:
            resolve_fn = lambda root, args, info: root.resolve(self.field_name, args, info)
        return resolve_fn(instance, args, info)

    @cached_property
    def type(self):
        if isinstance(self.field_type, Field):
            field_type = self.field_type.type
        else:
            field_type = get_object_type(self.field_type, self.object_type)
        field_type = self.type_wrapper(field_type)
        return field_type

    def type_wrapper(self, field_type):
        if not self.null:
            field_type = GraphQLNonNull(field_type)
        return field_type

    @cached_property
    def field(self):
        if not self.field_type:
            raise Exception('Must specify a field GraphQL type for the field %s'%self.field_name)

        if not self.object_type:
            raise Exception('Field could not be constructed in a non graphene.Type or graphene.Interface')

        extra_args = self.extra_args.copy()
        for arg_name, arg_value in extra_args.items():
            if isinstance(arg_value, GraphQLArgument):
                self.args[arg_name] = arg_value
                del extra_args[arg_name]

        if extra_args != {}:
            raise TypeError("Field %s.%s initiated with invalid args: %s" % (
                self.object_type,
                self.field_name,
                ','.join(meta_attrs.keys())
            ))

        return GraphQLField(
            self.type,
            description=self.description,
            args=self.args,
            resolver=self.resolver,
        )

    def __str__(self):
        """ Return "object_type.field_name". """
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


class ListField(Field):
    def type_wrapper(self, field_type):
        return GraphQLList(field_type)


class NonNullField(Field):
    def type_wrapper(self, field_type):
        return GraphQLNonNull(field_type)
