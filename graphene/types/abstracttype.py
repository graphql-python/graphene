import six

from ..utils.is_base_type import is_base_type
from .options import Options
from .utils import get_base_fields, merge, yank_fields_from_attrs


class AbstractTypeMeta(type):
    '''
    AbstractType Definition

    When we want to share fields across multiple types, like a Interface,
    a ObjectType and a Input ObjectType we can use AbstractTypes for defining
    our fields that the other types will inherit from.
    '''

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # AbstractType
        if not is_base_type(bases, AbstractTypeMeta):
            return type.__new__(cls, name, bases, attrs)

        for base in bases:
            if not issubclass(base, AbstractType) and issubclass(type(base), AbstractTypeMeta):
                # raise Exception('You can only extend AbstractTypes after the base definition.')
                return type.__new__(cls, name, bases, attrs)

        base_fields = get_base_fields(bases, _as=None)

        fields = yank_fields_from_attrs(attrs, _as=None)

        options = Options(
            fields=merge(base_fields, fields)
        )
        cls = type.__new__(cls, name, bases, dict(attrs, _meta=options))

        return cls


class AbstractType(six.with_metaclass(AbstractTypeMeta)):
    pass
