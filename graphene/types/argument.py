import copy
from collections import OrderedDict
import inspect
from itertools import chain

from graphql import GraphQLArgument
from graphql.utils.assert_valid_name import assert_valid_name

from ..utils.orderedtype import OrderedType


class Argument(GraphQLArgument, OrderedType):

    def __init__(self, type, default_value=None, description=None, name=None, _creation_counter=None):
        self.name = name
        self.type = type
        self.default_value = default_value
        self.description = description
        OrderedType.__init__(self, _creation_counter)

    @property
    def name(self):
        return self._name

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


def to_arguments(*args, **extra):
    from .proxy import TypeProxy
    args = list(filter(None, args)) + [extra]
    arguments = []
    iter_arguments = chain(*[arg.items() for arg in args])
    arguments_names = set()
    for default_name, arg in iter_arguments:
        if isinstance(arg, TypeProxy):
            arg = arg.as_argument()

        if not isinstance(arg, GraphQLArgument):
            raise ValueError('Unknown argument "{}".'.format(default_name))

        arg = copy.copy(arg)
        arg.name = arg.name or default_name
        assert arg.name, 'All arguments must have a name.'
        assert arg.name not in arguments_names, 'More than one Argument have same name "{}".'.format(arg.name)
        arguments.append(arg)
        arguments_names.add(arg.name)

    return OrderedDict([(a.name, a) for a in sorted(arguments)])
