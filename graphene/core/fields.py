from .types.field import Field
from .types.scalars import String, Int, Boolean, ID, Float
from .types.definitions import List, NonNull


class DeprecatedField(object):
    def __init__(self, *args, **kwargs):
        print("Using {} is not longer supported".format(self.__class__.__name__))
        kwargs['resolver'] = kwargs.pop('resolve', None)
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
