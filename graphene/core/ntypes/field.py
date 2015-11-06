from collections import OrderedDict

from graphql.core.type import GraphQLField, GraphQLInputObjectField

from .base import OrderedType
from .argument import to_arguments
from ...utils import to_camel_case
from ..types import BaseObjectType, InputObjectType


class Field(OrderedType):
    def __init__(self, type, description=None, args=None, name=None, resolver=None, *args_list, **kwargs):
        _creation_counter = kwargs.pop('_creation_counter', None)
        super(Field, self).__init__(_creation_counter=_creation_counter)
        self.name = name
        self.type = type
        self.description = description
        args = OrderedDict(args or {}, **kwargs)
        self.arguments = to_arguments(*args_list, **args)
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

    def internal_type(self, schema):
        return GraphQLField(schema.T(self.type), args=self.get_arguments(schema), resolver=self.resolver,
                            description=self.description,)

    def get_arguments(self, schema):
        if not self.arguments:
            return None

        return OrderedDict([(arg.name, schema.T(arg)) for arg in self.arguments])


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
