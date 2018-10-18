import inspect
from graphql.error import GraphQLError
from collections import Mapping, OrderedDict
from functools import partial

from .argument import Argument, to_arguments
from .mountedtype import MountedType
from .structures import NonNull
from .unmountedtype import UnmountedType
from .utils import get_type

base_type = type


def source_resolver(source, root, info, **args):
    resolved = getattr(root, source, None)
    if inspect.isfunction(resolved) or inspect.ismethod(resolved):
        return resolved()
    return resolved


class Field(MountedType):
    def __init__(
        self,
        type,
        args=None,
        resolver=None,
        source=None,
        deprecation_reason=None,
        name=None,
        description=None,
        required=False,
        _creation_counter=None,
        default_value=None,
        permission_classes=[],
        **extra_args
    ):
        super(Field, self).__init__(_creation_counter=_creation_counter)
        assert not args or isinstance(args, Mapping), (
            'Arguments in a field have to be a mapping, received "{}".'
        ).format(args)
        assert not (
            source and resolver
        ), "A Field cannot have a source and a resolver in at the same time."
        assert not callable(default_value), (
            'The default value can not be a function but received "{}".'
        ).format(base_type(default_value))

        if required:
            type = NonNull(type)

        # Check if name is actually an argument of the field
        if isinstance(name, (Argument, UnmountedType)):
            extra_args["name"] = name
            name = None

        # Check if source is actually an argument of the field
        if isinstance(source, (Argument, UnmountedType)):
            extra_args["source"] = source
            source = None

        self.name = name
        self._type = type
        self.args = to_arguments(args or OrderedDict(), extra_args)
        if source:
            resolver = partial(source_resolver, source)
        self.resolver = resolver
        self.deprecation_reason = deprecation_reason
        self.description = description
        self.default_value = default_value
        self.permission_classes = permission_classes

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this field requires.
        """
        return [permission() for permission in self.permission_classes]

    def check_permissions(self, info):
        for permission in self.get_permissions():
            if not permission.has_permission(info, self):
                self.permission_denied(
                    info, message=getattr(permission, 'message', None)
                )

    def permission_denied(self, info, message=None):
        raise GraphQLError(message)

    @property
    def type(self):
        return get_type(self._type)

    def get_resolver(self, parent_resolver):
        _resolver = self.resolver or parent_resolver

        if not _resolver:
            return None

        def resolver(root, info, *args, **kwargs):

            # TODO: pass root?
            self.check_permissions(info)

            return _resolver(root, info, *args, **kwargs)

        return resolver
