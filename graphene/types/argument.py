import inspect
from collections import OrderedDict
from itertools import chain

from graphql.type.definition import GraphQLArgument, GraphQLArgumentDefinition
from graphql.utils.assert_valid_name import assert_valid_name

from ..utils.orderedtype import OrderedType
from ..utils.str_converters import to_camel_case


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

    @classmethod
    def copy_from(cls, argument):
        if isinstance (argument, (GraphQLArgumentDefinition, Argument)):
            name = argument.name
        else:
            name = None
        return cls(
            type=argument.type,
            default_value=argument.default_value,
            description=argument.description,
            name=name,
            _creation_counter=argument.creation_counter if isinstance(argument, Argument) else None,
        )


def to_arguments(*args, **extra):
    from .unmountedtype import UnmountedType
    args = list(filter(None, args)) + [extra]
    arguments = []
    iter_arguments = chain(*[arg.items() for arg in args])
    arguments_names = set()
    for default_name, arg in iter_arguments:
        if isinstance(arg, UnmountedType):
            arg = arg.as_argument()

        if not isinstance(arg, GraphQLArgument):
            raise ValueError('Unknown argument "{}".'.format(default_name))

        arg = Argument.copy_from(arg)
        arg.name = arg.name or default_name and to_camel_case(default_name)
        assert arg.name, 'All arguments must have a name.'
        assert arg.name not in arguments_names, 'More than one Argument have same name "{}".'.format(arg.name)
        arguments.append(arg)
        arguments_names.add(arg.name)

    return OrderedDict([(a.name, a) for a in sorted(arguments)])
