from itertools import chain

from graphql.type import GraphQLArgument

from .base import ArgumentType, GroupNamedType, NamedType, OrderedType


class Argument(NamedType, OrderedType):

    def __init__(self, type, description=None, default=None,
                 name=None, _creation_counter=None):
        super(Argument, self).__init__(name=name, _creation_counter=_creation_counter)
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

    for default_name, arg in iter_arguments:
        if isinstance(arg, Argument):
            argument = arg
        elif isinstance(arg, ArgumentType):
            argument = arg.as_argument()
        else:
            raise ValueError('Unknown argument %s=%r' % (default_name, arg))

        if default_name:
            argument.default_name = default_name

        name = argument.name or argument.default_name
        assert name, 'Argument in field must have a name'
        assert name not in arguments, 'Found more than one Argument with same name {}'.format(name)
        arguments[name] = argument

    return sorted(arguments.values())
