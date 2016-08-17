import six

from ..utils.is_base_type import is_base_type
from .options import Options


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

        return type.__new__(cls, name, bases, dict(attrs, _meta=options))

    def __str__(cls):  # noqa: N805
        return cls._meta.name


class Union(six.with_metaclass(UnionMeta)):
    '''
    Union Type Definition

    When a field can return one of a heterogeneous set of types, a Union type
    is used to describe what types are possible as well as providing a function
    to determine which type is actually used when the field is resolved.
    '''

    resolve_type = None

    def __init__(self, *args, **kwargs):
        raise Exception("An Union cannot be intitialized")
