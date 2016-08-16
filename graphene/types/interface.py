import six

from ..utils.is_base_type import is_base_type
from .abstracttype import AbstractTypeMeta
from .options import Options
from .utils import (get_fields_in_type, yank_fields_from_attrs,
                    get_base_fields, merge)


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

        options.base_fields = get_base_fields(Interface, bases)

        if not options.local_fields:
            options.local_fields = get_fields_in_type(Interface, attrs)
            yank_fields_from_attrs(attrs, options.local_fields)

        options.fields = merge(
            options.base_fields,
            options.local_fields
        )

        return type.__new__(cls, name, bases, dict(attrs, _meta=options))

    def __str__(cls):  # noqa: N802
        return cls._meta.name


class Interface(six.with_metaclass(InterfaceMeta)):
    resolve_type = None

    def __init__(self, *args, **kwargs):
        raise Exception("An Interface cannot be intitialized")

    @classmethod
    def implements(cls, objecttype):
        pass
