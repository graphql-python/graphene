from collections import OrderedDict
import six

from ..utils.is_base_type import is_base_type
from .options import Options
from .utils import (get_fields_in_type, get_base_fields,
                    yank_fields_from_attrs, merge)


class AbstractTypeMeta(type):

    def __new__(cls, name, bases, attrs):
        from .interface import Interface
        # Also ensure initialization is only performed for subclasses of
        # AbstractType
        if not is_base_type(bases, AbstractTypeMeta):
            return type.__new__(cls, name, bases, attrs)

        print('-----> in AbstractTypeMeta')
        print(attrs.get('_meta'))
        print(attrs.get('Meta'))
        print(dir(attrs.get('Meta')))

        for base in bases:
            if not issubclass(base, AbstractType) and issubclass(type(base), AbstractTypeMeta):
                # raise Exception('You can only extend AbstractTypes after the base definition.')
                return type.__new__(cls, name, bases, attrs)

        _meta = attrs.pop('_meta', None)
        options = _meta or Options(
            attrs.pop('Meta', None),
            interfaces=(),
            fields=()
        )
        print('options:')
        print(options)

        options.base_fields = get_base_fields(AbstractType, bases)

        options.local_fields = get_fields_in_type(AbstractType, attrs)
        yank_fields_from_attrs(attrs, options.local_fields)

        options.interface_fields = OrderedDict()

        for interface in options.interfaces:
            assert issubclass(interface, Interface), (
                'All interfaces of {} must be a subclass of Interface. Received "{}".'
            ).format(name, interface)
            options.interface_fields.update(interface._meta.fields)

        options.fields = merge(
            options.interface_fields,
            options.base_fields,
            options.local_fields
        )

        # options = Options(
        #     fields=merge(base_fields, fields),
        #     interfaces=(),
        # )
        cls = type.__new__(cls, name, bases, dict(attrs, _meta=options))

        for interface in options.interfaces:
            interface.implements(cls)

        return cls


class AbstractType(six.with_metaclass(AbstractTypeMeta)):
    pass
