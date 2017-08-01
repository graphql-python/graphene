from collections import OrderedDict

from .base import BaseOptions, BaseType
from .inputfield import InputField
from .unmountedtype import UnmountedType
from .utils import yank_fields_from_attrs


class InputObjectTypeOptions(BaseOptions):
    fields = None  # type: Dict[str, Field]
    create_container = None  # type: Callable


class InputObjectTypeContainer(dict, BaseType):
    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        for key, value in self.items():
            setattr(self, key, value)

    def __init_subclass__(cls, *args, **kwargs):
        pass


class InputObjectType(UnmountedType, BaseType):
    '''
    Input Object Type Definition

    An input object defines a structured collection of fields which may be
    supplied to a field argument.

    Using `NonNull` will ensure that a value must be provided by the query
    '''

    @classmethod
    def __init_subclass_with_meta__(cls, container=None, **options):
        _meta = InputObjectTypeOptions(cls)

        fields = OrderedDict()
        for base in reversed(cls.__mro__):
            fields.update(
                yank_fields_from_attrs(base.__dict__, _as=InputField)
            )

        _meta.fields = fields
        if container is None:
            container = type(cls.__name__, (InputObjectTypeContainer, cls), {})
        _meta.container = container
        super(InputObjectType, cls).__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def get_type(cls):
        '''
        This function is called when the unmounted type (InputObjectType instance)
        is mounted (as a Field, InputField or Argument)
        '''
        return cls
