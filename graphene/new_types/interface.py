import six
from collections import OrderedDict

from ..utils.is_base_type import is_base_type
from .options import Options

from .utils import get_fields_in_type, attrs_without_fields


class InterfaceMeta(type):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # ObjectType
        if not is_base_type(bases, InterfaceMeta):
            return type.__new__(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=name,
            description=attrs.get('__doc__'),
        )

        fields = get_fields_in_type(Interface, attrs)
        options.fields = OrderedDict(sorted(fields, key=lambda f: f[1]))

        attrs = attrs_without_fields(attrs, fields)
        cls = super(InterfaceMeta, cls).__new__(cls, name, bases, dict(attrs, _meta=options))

        return cls


class Interface(six.with_metaclass(InterfaceMeta)):
    resolve_type = None

    def __init__(self, *args, **kwargs):
        raise Exception("An interface cannot be intitialized")

    @classmethod
    def implements(cls, objecttype):
        pass
