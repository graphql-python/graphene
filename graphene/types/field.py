import inspect

from graphql.type import GraphQLField, GraphQLInputObjectField
from graphql.utils.assert_valid_name import assert_valid_name

from ..utils.orderedtype import OrderedType
from ..utils.str_converters import to_camel_case
from .argument import to_arguments


class AbstractField(object):

    @property
    def name(self):
        return self._name or self.attname and to_camel_case(self.attname)

    @name.setter
    def name(self, name):
        if name is not None:
            assert_valid_name(name)
        self._name = name

    @property
    def type(self):
        from ..utils.get_graphql_type import get_graphql_type
        from .structures import NonNull
        if inspect.isfunction(self._type):
            _type = self._type()
        else:
            _type = self._type

        if self.required:
            return NonNull(_type)
        return get_graphql_type(_type)

    @type.setter
    def type(self, type):
        self._type = type


class Field(AbstractField, GraphQLField, OrderedType):

    def __init__(self, type, args=None, resolver=None, source=None, deprecation_reason=None,
                 name=None, description=None, required=False, _creation_counter=None, **extra_args):
        self.name = name
        self.attname = None
        self.parent = None
        self.type = type
        self.args = to_arguments(args, extra_args)
        assert not (source and resolver), ('You cannot have a source '
                                           'and a resolver at the same time')

        self.resolver = resolver
        self.source = source
        self.required = required
        self.deprecation_reason = deprecation_reason
        self.description = description
        OrderedType.__init__(self, _creation_counter=_creation_counter)

    def mount_error_message(self, where):
        return 'Field "{}" can only be mounted in ObjectType or Interface, received {}.'.format(
            self,
            where.__name__
        )

    def mount(self, parent, attname=None):
        from .objecttype import ObjectType
        from .interface import Interface
        assert issubclass(parent, (ObjectType, Interface)), self.mount_error_message(parent)

        self.attname = attname
        self.parent = parent

    def default_resolver(self, root, args, context, info):
        return getattr(root, self.source or self.attname, None)

    @property
    def resolver(self):
        resolver = getattr(self.parent, 'resolve_{}'.format(self.attname), None)

        # We try to get the resolver from the interfaces
        # This is not needed anymore as Interfaces could be extended now with Python syntax
        # if not resolver and issubclass(self.parent, ObjectType):
        #     graphql_type = self.parent._meta.graphql_type
        #     interfaces = graphql_type._provided_interfaces or []
        #     for interface in interfaces:
        #         if not isinstance(interface, GrapheneInterfaceType):
        #             continue
        #         fields = interface.get_fields()
        #         if self.attname in fields:
        #             resolver = getattr(interface.graphene_type, 'resolve_{}'.format(self.attname), None)
        #             if resolver:
        #                 # We remove the bounding to the method
        #                 resolver = resolver #.__func__
        #                 break

        if resolver:
            resolver = getattr(resolver, '__func__', resolver)
        else:
            resolver = self.default_resolver

        # def resolver_wrapper(root, *args, **kwargs):
        #     if not isinstance(root, self.parent):
        #         root = self.parent()
        #     return resolver(root, *args, **kwargs)

        return self._resolver or resolver  # resolver_wrapper

    @resolver.setter
    def resolver(self, resolver):
        self._resolver = resolver

    def __copy__(self):
        return self.copy_and_extend(self)

    @classmethod
    def copy_and_extend(
            cls, field, type=None, args=None, resolver=None, source=None, deprecation_reason=None, name=None,
            description=None, required=False, _creation_counter=False, parent=None, attname=None, **extra_args):
        if isinstance(field, Field):
            type = type or field._type
            resolver = resolver or field._resolver
            source = source or field.source
            name = name or field._name
            required = required or field.required
            _creation_counter = field.creation_counter if _creation_counter is False else None
            attname = attname or field.attname
            parent = parent or field.parent
        else:
            # If is a GraphQLField
            type = type or field.type
            resolver = resolver or field.resolver
            name = field.name
            _creation_counter = None
            attname = attname or name
            parent = parent

        new_field = cls(
            type=type,
            args=to_arguments(args, field.args),
            resolver=resolver,
            source=source,
            deprecation_reason=field.deprecation_reason,
            name=name,
            required=required,
            description=field.description,
            _creation_counter=_creation_counter,
            **extra_args
        )
        new_field.attname = attname
        new_field.parent = parent
        return new_field

    def __str__(self):
        if not self.parent:
            return 'Not bounded field'
        return "{}.{}".format(self.parent._meta.graphql_type, self.attname)


class InputField(AbstractField, GraphQLInputObjectField, OrderedType):

    def __init__(self, type, default_value=None, description=None, name=None, required=False, _creation_counter=None):
        self.name = name
        self.type = type
        self.default_value = default_value
        self.description = description
        self.required = required
        self.attname = None
        self.parent = None
        OrderedType.__init__(self, _creation_counter=_creation_counter)

    def mount_error_message(self, where):
        return 'InputField {} can only be mounted in InputObjectType classes, received {}.'.format(
            self,
            where.__name__
        )

    def mount(self, parent, attname):
        from .inputobjecttype import InputObjectType

        assert issubclass(parent, (InputObjectType)), self.mount_error_message(parent)
        self.attname = attname
        self.parent = parent

    def __copy__(self):
        return self.copy_and_extend(self)

    @classmethod
    def copy_and_extend(cls, field, type=None, default_value=None, description=None, name=None,
                        required=False, parent=None, attname=None, _creation_counter=False):
        if isinstance(field, Field):
            type = type or field._type
            name = name or field._name
            required = required or field.required
            _creation_counter = field.creation_counter if _creation_counter is False else None
            attname = attname or field.attname
            parent = parent or field.parent
        else:
            # If is a GraphQLField
            type = type or field.type
            name = field.name
            _creation_counter = None

        new_field = cls(
            type=type,
            name=name,
            required=required,
            default_value=default_value or field.default_value,
            description=description or field.description,
            _creation_counter=_creation_counter,
        )
        new_field.attname = attname
        new_field.parent = parent
        return new_field
