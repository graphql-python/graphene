import warnings

from .types.base import FieldType
from .types.field import Field
from .types.scalars import String, Int, Boolean, ID, Float
from .types.definitions import List, NonNull


class DeprecatedField(FieldType):
    def __init__(self, *args, **kwargs):
        cls = self.__class__
        warnings.warn("Using {} is not longer supported".format(cls.__name__)
                      , FutureWarning)
        kwargs['resolver'] = kwargs.pop('resolve', None)
        self.required = kwargs.pop('required', False)
        return super(DeprecatedField, self).__init__(*args, **kwargs)

    def as_field(self):
        t = self
        if self.required:
            t = NonNull(t)
        return Field(t, _creation_counter=self.creation_counter, *self.args, **self.kwargs)


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
