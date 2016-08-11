import six
from collections import OrderedDict

from ..utils.is_base_type import is_base_type
from .options import Options

from .utils import get_fields_in_type, attrs_without_fields


def merge_fields_in_attrs(bases, attrs):
    for base in bases:
        if not issubclass(base, AbstractType):
            continue
        for name, field in base._meta.fields.items():
            if name in attrs:
                continue
            attrs[name] = field
    return attrs


class AbstractTypeMeta(type):

    def __new__(cls, name, bases, attrs):
        options = attrs.get('_meta', Options())

        attrs = merge_fields_in_attrs(bases, attrs)
        fields = get_fields_in_type(cls, attrs)
        options.fields = OrderedDict(sorted(fields, key=lambda f: f[1]))

        attrs = attrs_without_fields(attrs, fields)
        cls = type.__new__(cls, name, bases, dict(attrs, _meta=options))

        return cls


class AbstractType(six.with_metaclass(AbstractTypeMeta)):
    pass
