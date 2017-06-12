from collections import OrderedDict

import six

from ..utils.is_base_type import is_base_type
from ..utils.trim_docstring import trim_docstring
from .abstracttype import AbstractTypeMeta
from .field import Field
from .interface import Interface
from .options import Options
from .utils import get_base_fields, merge, yank_fields_from_attrs


class ObjectTypeMeta(AbstractTypeMeta):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # ObjectType
        if not is_base_type(bases, ObjectTypeMeta):
            return type.__new__(cls, name, bases, attrs)

        _meta = attrs.pop('_meta', None)
        defaults = dict(
            name=name,
            description=trim_docstring(attrs.get('__doc__')),
            interfaces=(),
            possible_types=(),
            default_resolver=None,
            local_fields=OrderedDict(),
        )
        if not _meta:
            options = Options(
                attrs.pop('Meta', None),
                **defaults
            )
        else:
            options = _meta.extend_with_defaults(defaults)

        options.base_fields = get_base_fields(bases, _as=Field)

        if not options.local_fields:
            options.local_fields = yank_fields_from_attrs(attrs=attrs, _as=Field)

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

        cls = type.__new__(cls, name, bases, dict(attrs, _meta=options))

        assert not (options.possible_types and cls.is_type_of), (
            '{}.Meta.possible_types will cause type collision with {}.is_type_of. '
            'Please use one or other.'
        ).format(name, name)

        for interface in options.interfaces:
            interface.implements(cls)

        return cls

    def __str__(cls):  # noqa: N802
        return cls._meta.name


class ObjectType(six.with_metaclass(ObjectTypeMeta)):
    '''
    Object Type Definition

    Almost all of the GraphQL types you define will be object types. Object types
    have a name, but most importantly describe their fields.
    '''

    is_type_of = None

    def __init__(self, *args, **kwargs):
        # ObjectType acting as container
        args_len = len(args)
        fields = self._meta.fields.items()
        if args_len > len(fields):
            # Daft, but matches old exception sans the err msg.
            raise IndexError("Number of args exceeds number of fields")
        fields_iter = iter(fields)

        if not kwargs:
            for val, (name, field) in zip(args, fields_iter):
                setattr(self, name, val)
        else:
            for val, (name, field) in zip(args, fields_iter):
                setattr(self, name, val)
                kwargs.pop(name, None)

        for name, field in fields_iter:
            try:
                val = kwargs.pop(name)
                setattr(self, name, val)
            except KeyError:
                pass

        if kwargs:
            for prop in list(kwargs):
                try:
                    if isinstance(getattr(self.__class__, prop), property) or prop.startswith('_'):
                        setattr(self, prop, kwargs.pop(prop))
                except AttributeError:
                    pass
            if kwargs:
                raise TypeError(
                    "'{}' is an invalid keyword argument for {}".format(
                        list(kwargs)[0],
                        self.__class__.__name__
                    )
                )
