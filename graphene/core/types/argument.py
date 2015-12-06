from collections import OrderedDict
from functools import wraps
from itertools import chain

from graphql.core.type import GraphQLArgument

from ...utils import ProxySnakeDict, to_camel_case
from .base import ArgumentType, GroupNamedType, NamedType, OrderedType


class Argument(NamedType, OrderedType):

    def __init__(self, type, description=None, default=None,
                 name=None, _creation_counter=None):
        super(Argument, self).__init__(_creation_counter=_creation_counter)
        self.name = name
        self.type = type
        self.description = description
        self.default = default

    def internal_type(self, schema):
        return GraphQLArgument(
            schema.T(self.type),
            self.default, self.description)

    def __repr__(self):
        return self.name


class ArgumentsGroup(GroupNamedType):

    def __init__(self, *args, **kwargs):
        arguments = to_arguments(*args, **kwargs)
        super(ArgumentsGroup, self).__init__(*arguments)


def to_arguments(*args, **kwargs):
    arguments = {}
    iter_arguments = chain(kwargs.items(), [(None, a) for a in args])

    for name, arg in iter_arguments:
        if isinstance(arg, Argument):
            argument = arg
        elif isinstance(arg, ArgumentType):
            argument = arg.as_argument()
        else:
            raise ValueError('Unknown argument %s=%r' % (name, arg))

        if name:
            argument.name = to_camel_case(name)
        assert argument.name, 'Argument in field must have a name'
        assert argument.name not in arguments, 'Found more than one Argument with same name {}'.format(
            argument.name)
        arguments[argument.name] = argument

    return sorted(arguments.values())


def snake_case_args(resolver):
    @wraps(resolver)
    def wrapped_resolver(instance, args, info):
        return resolver(instance, ProxySnakeDict(args), info)

    return wrapped_resolver
