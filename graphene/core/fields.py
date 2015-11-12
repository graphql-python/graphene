import warnings

from .types.base import FieldType
from .types.definitions import List, NonNull
from .types.field import Field
from .types.scalars import ID, Boolean, Float, Int, String


class DeprecatedField(FieldType):

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        warnings.warn("Using {} is not longer supported".format(
            cls.__name__), FutureWarning)
        if 'resolve' in kwargs:
            kwargs['resolver'] = kwargs.pop('resolve')
        return super(DeprecatedField, self).__init__(*args, **kwargs)


class StringField(DeprecatedField, String):
    pass


class IntField(DeprecatedField, Int):
    pass


class BooleanField(DeprecatedField, Boolean):
    pass


class IDField(DeprecatedField, ID):
    pass


class FloatField(DeprecatedField, Float):
    pass


class ListField(DeprecatedField, List):
    pass


class NonNullField(DeprecatedField, NonNull):
    pass


__all__ = ['Field', 'StringField', 'IntField', 'BooleanField',
           'IDField', 'FloatField', 'ListField', 'NonNullField']
