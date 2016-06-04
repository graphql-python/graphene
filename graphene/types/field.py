import inspect

from graphql import GraphQLField
from graphql.utils.assert_valid_name import assert_valid_name

from .objecttype import ObjectType
from .interface import Interface
from ..utils.orderedtype import OrderedType


class Field(GraphQLField, OrderedType):
    __slots__ = ('_name', '_type', '_args', '_resolver', 'deprecation_reason', 'description', 'source', '_extra_args', 'attname', 'parent', 'creation_counter')

    def __init__(self, type, args=None, resolver=None, source=None, deprecation_reason=None, name=None, description=None, **extra_args):
        self.name = name
        self.attname = None
        self.parent = None
        self.type = type
        self.args = args
        assert not (source and resolver), ('You cannot have a source '
                                           'and a resolver at the same time')

        self.resolver = resolver
        self.source = source
        self.deprecation_reason = deprecation_reason
        self.description = description
        self._extra_args = extra_args
        OrderedType.__init__(self)

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
        return self._name or self.attname

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
    def args(self):
        return self._args

    @args.setter
    def args(self, args):
        self._args = args

    @property
    def resolver(self):
        return self._resolver or getattr(self.parent(), 'resolve_{}'.format(self.attname), None)

    @resolver.setter
    def resolver(self, resolver):
        self._resolver = resolver
