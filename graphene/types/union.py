import six

from ..utils.is_base_type import is_base_type
from ..utils.trim_docstring import trim_docstring
from .options import Options
from .unmountedtype import UnmountedType


class UnionMeta(type):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # Union
        if not is_base_type(bases, UnionMeta):
            return type.__new__(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=name,
            description=trim_docstring(attrs.get('__doc__')),
            types=(),
        )

        assert (
            isinstance(options.types, (list, tuple)) and
            len(options.types) > 0
        ), 'Must provide types for Union {}.'.format(options.name)

        return type.__new__(cls, name, bases, dict(attrs, _meta=options))

    def __str__(cls):  # noqa: N805
        return cls._meta.name


class Union(six.with_metaclass(UnionMeta, UnmountedType)):
    '''
    Union Type Definition

    When a field can return one of a heterogeneous set of types, a Union type
    is used to describe what types are possible as well as providing a function
    to determine which type is actually used when the field is resolved.
    '''

    @classmethod
    def get_type(cls):
        '''
        This function is called when the unmounted type (Union instance)
        is mounted (as a Field, InputField or Argument)
        '''
        return cls

    @classmethod
    def resolve_type(cls, instance, context, info):
        from .objecttype import ObjectType
        if isinstance(instance, ObjectType):
            return type(instance)
