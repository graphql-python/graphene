import inspect
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
    """
    Makes a field available on an ObjectType in the GraphQL schema. Any type can be mounted as a
    Field:

    - Object Type
    - Scalar Type
    - Enum
    - Interface
    - Union

    All class attributes of ``graphene.ObjectType`` are implicitly mounted as Field using the below
    arguments.

    .. code:: python

        class Person(ObjectType):
            first_name = graphene.String(required=True)                # implicitly mounted as Field
            last_name = graphene.Field(String, description='Surname')  # explicitly mounted as Field

    args:
        type (class for a graphene.UnmountedType): must be a class (not an instance) of an
            unmounted graphene type (ex. scalar or object) which is used for the type of this
            field in the GraphQL schema.
        args (optional, Dict[str, graphene.Argument]): arguments that can be input to the field.
            Prefer to use **extra_args.
        resolver (optional, Callable): A function to get the value for a Field from the parent
            value object. If not set, the default resolver method for the schema is used.
        source (optional, str): attribute name to resolve for this field from the parent value
            object. Alternative to resolver (cannot set both source and resolver).
        deprecation_reason (optional, str): Setting this value indicates that the field is
            depreciated and may provide instruction or reason on how for clients to proceed.
        required (optional, bool): indicates this field as not null in the graphql scehma. Same behavior as
            graphene.NonNull. Default False.
        name (optional, str): the name of the GraphQL field (must be unique in a type). Defaults to attribute
            name.
        description (optional, str): the description of the GraphQL field in the schema.
        default_value (optional, Any): Default value to resolve if none set from schema.
        **extra_args (optional, Dict[str, Union[graphene.Argument, graphene.UnmountedType]): any
            additional arguments to mount on the field.
    """

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

    @property
    def type(self):
        return get_type(self._type)

    def get_resolver(self, parent_resolver):
        return self.resolver or parent_resolver
