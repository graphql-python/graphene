from collections import OrderedDict

import six

from graphene.utils.subclass_with_meta import SubclassWithMeta_Meta

from ..pyutils.compat import Enum as PyEnum
from .base import BaseOptions, BaseType
from .unmountedtype import UnmountedType


def eq_enum(self, other):
    if isinstance(other, self.__class__):
        return self is other
    return self.value is other


EnumType = type(PyEnum)


class EnumOptions(BaseOptions):
    enum = None  # type: Enum
    deprecation_reason = None


def _filter_magic_members(classdict):
    def is_special(name):
        # We also remove the Meta attribute from the class to not collide
        # with the enum values.
        if name == "Meta":
            return True
        return name[:2] == name[-2:] == "__"

    return OrderedDict((k, v) for k, v in classdict.items() if not is_special(k))


class EnumMeta(SubclassWithMeta_Meta):
    def __new__(cls, name, bases, classdict, **options):
        meta_class = classdict.get("Meta")
        if meta_class is None or not hasattr(meta_class, "legacy_enum_resolver"):
            is_legacy = True
        else:
            is_legacy = meta_class.legacy_enum_resolver

        enum_members = _filter_magic_members(classdict)
        if is_legacy:
            enum_members["__eq__"] = eq_enum
        enum = PyEnum(name, enum_members)
        return SubclassWithMeta_Meta.__new__(
            cls, name, bases, OrderedDict(classdict, __enum__=enum), **options
        )

    def get(cls, value):
        return cls._meta.enum(value)

    def __getitem__(cls, value):
        return cls._meta.enum[value]

    def __prepare__(name, bases, **kwargs):  # noqa: N805
        return OrderedDict()

    def __call__(cls, *args, **kwargs):  # noqa: N805
        if cls is Enum:
            description = kwargs.pop("description", None)
            return cls.from_enum(PyEnum(*args, **kwargs), description=description)
        return super(EnumMeta, cls).__call__(*args, **kwargs)

    def from_enum(cls, enum, description=None, deprecation_reason=None, legacy_enum_resolver=True):  # noqa: N805
        description = description or enum.__doc__
        meta_dict = {
            "enum": enum,
            "description": description,
            "deprecation_reason": deprecation_reason,
            "legacy_enum_resolver": legacy_enum_resolver,
        }
        meta_class = type("Meta", (object,), meta_dict)
        return type(meta_class.enum.__name__, (Enum,), {"Meta": meta_class})


class Enum(six.with_metaclass(EnumMeta, UnmountedType, BaseType)):
    @classmethod
    def __init_subclass_with_meta__(cls, enum=None, _meta=None, **options):
        if not _meta:
            _meta = EnumOptions(cls)
        _meta.enum = enum or cls.__enum__
        _meta.deprecation_reason = options.pop("deprecation_reason", None)
        _meta.legacy_enum_resolver = options.pop("legacy_enum_resolver", True)
        for key, value in _meta.enum.__members__.items():
            setattr(cls, key, value)

        super(Enum, cls).__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def get_type(cls):
        """
        This function is called when the unmounted type (Enum instance)
        is mounted (as a Field, InputField or Argument)
        """
        return cls
