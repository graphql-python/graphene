import inspect

from graphql import GraphQLField
from graphql.utils.assert_valid_name import assert_valid_name

from .objecttype import ObjectType
from .interface import Interface
from ..utils.orderedtype import OrderedType
from ..utils.str_converters import to_camel_case
from .argument import to_arguments


class Field(GraphQLField, OrderedType):
    __slots__ = ('_name', '_type', '_args', '_resolver', 'deprecation_reason', 'description', 'source', 'attname', 'parent', 'creation_counter')

    def __init__(self, type, args=None, resolver=None, source=None, deprecation_reason=None, name=None, description=None, _creation_counter=None, **extra_args):
        self.name = name
        self.attname = None
        self.parent = None
        self.type = type
        self.args = to_arguments(args, extra_args)
        assert not (source and resolver), ('You cannot have a source '
                                           'and a resolver at the same time')

        self.resolver = resolver
        self.source = source
        self.deprecation_reason = deprecation_reason
        self.description = description
        OrderedType.__init__(self, _creation_counter=_creation_counter)

    def contribute_to_class(self, cls, attname):
        assert issubclass(cls, (ObjectType, Interface)), 'Field {} cannot be mounted in {}'.format(
            self,
            cls
        )
        self.attname = attname
        self.parent = cls
        add_field = getattr(cls._meta.graphql_type, "add_field", None)
        assert add_field, "Field {} cannot be mounted in {}".format(self, cls)
        add_field(self)

    @property
    def name(self):
        return self._name or to_camel_case(self.attname)

    @name.setter
    def name(self, name):
        if name is not None:
            assert_valid_name(name)
        self._name = name

    @property
    def type(self):
        from ..utils.get_graphql_type import get_graphql_type
        if inspect.isfunction(self._type):
            return get_graphql_type(self._type())
        return get_graphql_type(self._type)

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def resolver(self):
        def default_resolver(root, args, context, info):
            return getattr(root, self.source or self.attname, None)

        resolver = getattr(self.parent, 'resolve_{}'.format(self.attname), default_resolver)

        def resolver_wrapper(root, *args, **kwargs):
            if not isinstance(root, self.parent):
                root = self.parent()
            return resolver(root, *args, **kwargs)

        return self._resolver or resolver_wrapper

    @resolver.setter
    def resolver(self, resolver):
        self._resolver = resolver

    def __copy__(self):
        field = Field(
            type=self._type,
            args=self.args,
            resolver=self._resolver,
            source=self.source,
            deprecation_reason=self.deprecation_reason,
            name=self._name,
            description=self.description,
            _creation_counter=self.creation_counter,
        )
        field.attname = self.attname
        field.parent = self.parent
        return field

    def __str__(self):
        if not self.parent:
            return 'Not bounded field'
        return "{}.{}".format(self.parent._meta.graphql_type, self.attname)
