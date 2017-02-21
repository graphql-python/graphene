import six

from ..utils.is_base_type import is_base_type
from ..utils.trim_docstring import trim_docstring
from .abstracttype import AbstractTypeMeta
from .inputfield import InputField
from .options import Options
from .unmountedtype import UnmountedType
from .utils import get_base_fields, merge, yank_fields_from_attrs


class InputObjectTypeMeta(AbstractTypeMeta):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # InputObjectType
        if not is_base_type(bases, InputObjectTypeMeta):
            return type.__new__(cls, name, bases, attrs)

        options = Options(
            attrs.pop('Meta', None),
            name=name,
            description=trim_docstring(attrs.get('__doc__')),
            local_fields=None,
        )

        options.base_fields = get_base_fields(bases, _as=InputField)

        if not options.local_fields:
            options.local_fields = yank_fields_from_attrs(attrs, _as=InputField)

        options.fields = merge(
            options.base_fields,
            options.local_fields
        )
        return type.__new__(cls, name, bases, dict(attrs, _meta=options))

    def __str__(cls):  # noqa: N802
        return cls._meta.name


class InputObjectType(six.with_metaclass(InputObjectTypeMeta, UnmountedType)):
    '''
    Input Object Type Definition

    An input object defines a structured collection of fields which may be
    supplied to a field argument.

    Using `NonNull` will ensure that a value must be provided by the query
    '''

    @classmethod
    def get_type(cls):
        '''
        This function is called when the unmounted type (InputObjectType instance)
        is mounted (as a Field, InputField or Argument)
        '''
        return cls
