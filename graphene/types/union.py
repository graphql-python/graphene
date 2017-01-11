import six
from functools import partial

from ..utils.is_base_type import is_base_type
from .options import Options


def get_default_connection(cls):
    from graphene.relay.connection import Connection

    class Meta:
        node = cls

    return type('{}Connection'.format(cls.__name__), (Connection,), {'Meta': Meta})


class UnionMeta(type):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # Union
        if not is_base_type(bases, UnionMeta):
            return type.__new__(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=name,
            description=attrs.get('__doc__'),
            types=(),
        )

        assert (
            isinstance(options.types, (list, tuple)) and
            len(options.types) > 0
        ), 'Must provide types for Union {}.'.format(options.name)

        cls = type.__new__(cls, name, bases, dict(attrs, _meta=options))

        get_connection = getattr(cls, 'get_connection', None)
        if not get_connection:
            get_connection = partial(get_default_connection, cls)

        cls.Connection = get_connection()

        return cls

    def __str__(cls):  # noqa: N805
        return cls._meta.name


class Union(six.with_metaclass(UnionMeta)):
    '''
    Union Type Definition

    When a field can return one of a heterogeneous set of types, a Union type
    is used to describe what types are possible as well as providing a function
    to determine which type is actually used when the field is resolved.
    '''

    @classmethod
    def resolve_type(cls, instance, context, info):
        from .objecttype import ObjectType
        if isinstance(instance, ObjectType):
            return type(instance)

    def __init__(self, *args, **kwargs):
        raise Exception("A Union cannot be intitialized")
