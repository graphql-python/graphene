from collections import OrderedDict

from .inputfield import InputField
from .unmountedtype import UnmountedType
from .utils import yank_fields_from_attrs

from .base import BaseOptions, BaseType


class InputObjectTypeOptions(BaseOptions):
    fields = None  # type: Dict[str, Field]


class InputObjectType(UnmountedType, BaseType):
    '''
    Input Object Type Definition

    An input object defines a structured collection of fields which may be
    supplied to a field argument.

    Using `NonNull` will ensure that a value must be provided by the query
    '''

    @classmethod
    def __init_subclass_with_meta__(cls, **options):
        _meta = InputObjectTypeOptions(cls)

        fields = OrderedDict()
        for base in reversed(cls.__mro__):
            fields.update(
                yank_fields_from_attrs(base.__dict__, _as=InputField)
            )

        _meta.fields = fields
        super(InputObjectType, cls).__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def get_type(cls):
        '''
        This function is called when the unmounted type (InputObjectType instance)
        is mounted (as a Field, InputField or Argument)
        '''
        return cls
