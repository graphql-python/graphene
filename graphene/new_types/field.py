import inspect
from functools import partial
from collections import OrderedDict, Mapping

from ..utils.orderedtype import OrderedType
from .structures import NonNull
from .argument import to_arguments


def source_resolver(source, root, args, context, info):
    resolved = getattr(root, source, None)
    if inspect.isfunction(resolved):
        return resolved()
    return resolved


class Field(OrderedType):

    def __init__(self, type, args=None, resolver=None, source=None,
                 deprecation_reason=None, name=None, description=None,
                 required=False, _creation_counter=None, **extra_args):
        super(Field, self).__init__(_creation_counter=_creation_counter)
        self.name = name
        # self.attname = None
        # self.parent = None
        if required:
            type = NonNull(type)
        self._type = type
        if args:
            assert isinstance(args, Mapping), 'Arguments in a field have to be a mapping, received "{}".'.format(args)
        self.args = to_arguments(args or OrderedDict(), extra_args)
        # self.args = to_arguments(args, extra_args)
        assert not (source and resolver), ('A Field cannot have a source and a '
                                           'resolver in at the same time.')
        if source:
            resolver = partial(source_resolver, source)
        self.resolver = resolver
        self.deprecation_reason = deprecation_reason
        self.description = description

    @property
    def type(self):
        if inspect.isfunction(self._type):
            return self._type()
        return self._type
