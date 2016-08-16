import six

from ..utils.is_base_type import is_base_type
from .options import Options
from .utils import (get_fields_in_type, get_base_fields,
                    yank_fields_from_attrs, merge)


class AbstractTypeMeta(type):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # AbstractType
        if not is_base_type(bases, AbstractTypeMeta):
            return type.__new__(cls, name, bases, attrs)

        for base in bases:
            if not issubclass(base, AbstractType) and issubclass(type(base), AbstractTypeMeta):
                # raise Exception('You can only extend AbstractTypes after the base definition.')
                return type.__new__(cls, name, bases, attrs)

        base_fields = get_base_fields(AbstractType, bases)

        fields = get_fields_in_type(AbstractType, attrs)
        yank_fields_from_attrs(attrs, fields)

        options = Options(
            fields=merge(base_fields, fields)
        )
        cls = type.__new__(cls, name, bases, dict(attrs, _meta=options))

        return cls


class AbstractType(six.with_metaclass(AbstractTypeMeta)):
    pass
