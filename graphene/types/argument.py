from collections import OrderedDict
from itertools import chain

from ..utils.orderedtype import OrderedType
from .structures import NonNull


class Argument(OrderedType):

    def __init__(self, type, default_value=None, description=None, name=None, required=False, _creation_counter=None):
        super(Argument, self).__init__(_creation_counter=_creation_counter)

        if required:
            type = NonNull(type)

        self.name = name
        self.type = type
        self.default_value = default_value
        self.description = description

    def __eq__(self, other):
        return isinstance(other, Argument) and (
            self.name == other.name,
            self.type == other.type,
            self.default_value == other.default_value,
            self.description == other.description
        )


def to_arguments(args, extra_args):
    from .unmountedtype import UnmountedType
    extra_args = sorted(extra_args.items(), key=lambda f: f[1])
    iter_arguments = chain(args.items(), extra_args)
    arguments = OrderedDict()
    for default_name, arg in iter_arguments:
        if isinstance(arg, UnmountedType):
            arg = arg.Argument()

        if not isinstance(arg, Argument):
            raise ValueError('Unknown argument "{}".'.format(default_name))

        arg_name = default_name or arg.name
        assert arg_name not in arguments, 'More than one Argument have same name "{}".'.format(arg_name)
        arguments[arg_name] = arg

    return arguments
