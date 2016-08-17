import six

from ..utils.is_base_type import is_base_type
from .abstracttype import AbstractTypeMeta
from .options import Options
from .utils import yank_fields_from_attrs, get_base_fields, merge
from .field import Field


class InterfaceMeta(AbstractTypeMeta):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # Interface
        if not is_base_type(bases, InterfaceMeta):
            return type.__new__(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=name,
            description=attrs.get('__doc__'),
            local_fields=None,
        )

        options.base_fields = get_base_fields(bases, _as=Field)

        if not options.local_fields:
            options.local_fields = yank_fields_from_attrs(attrs, _as=Field)

        options.fields = merge(
            options.base_fields,
            options.local_fields
        )

        return type.__new__(cls, name, bases, dict(attrs, _meta=options))

    def __str__(cls):  # noqa: N802
        return cls._meta.name


class Interface(six.with_metaclass(InterfaceMeta)):
    '''
    Interface Type Definition

    When a field can return one of a heterogeneous set of types, a Interface type
    is used to describe what types are possible, what fields are in common across
    all types, as well as a function to determine which type is actually used
    when the field is resolved.
    '''

    resolve_type = None

    def __init__(self, *args, **kwargs):
        raise Exception("An Interface cannot be intitialized")

    @classmethod
    def implements(cls, objecttype):
        pass
