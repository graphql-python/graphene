from itertools import chain

from graphql.core.type import GraphQLArgument

from .base import OrderedType, ArgumentType
from ...utils import to_camel_case


class Argument(OrderedType):
    def __init__(self, type, description=None, default=None, name=None, _creation_counter=None):
        super(Argument, self).__init__(_creation_counter=_creation_counter)
        self.name = name
        self.type = type
        self.description = description
        self.default = default

    def internal_type(self, schema):
        return GraphQLArgument(schema.T(self.type), self.default, self.description)

    def __repr__(self):
        return self.name


def to_arguments(*args, **kwargs):
    arguments = {}
    iter_arguments = chain(kwargs.items(), [(None, a) for a in args])

    for name, arg in iter_arguments:
        if isinstance(arg, Argument):
            argument = arg
        elif isinstance(arg, ArgumentType):
            argument = arg.as_argument()
        else:
            raise ValueError('Unknown argument value type %r' % arg)

        if name:
            argument.name = to_camel_case(name)
        assert argument.name, 'Argument in field must have a name'
        assert argument.name not in arguments, 'Found more than one Argument with same name {}'.format(argument.name)
        arguments[argument.name] = argument

    return sorted(arguments.values())
