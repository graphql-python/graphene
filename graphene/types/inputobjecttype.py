from collections import OrderedDict

from .base import BaseOptions, BaseType
from .inputfield import InputField
from .unmountedtype import UnmountedType
from .utils import yank_fields_from_attrs


class InputObjectTypeOptions(BaseOptions):
    fields = None  # type: Dict[str, Field]
    create_container = None  # type: Callable


class InputObjectType(dict, UnmountedType, BaseType):
    '''
    Input Object Type Definition

    An input object defines a structured collection of fields which may be
    supplied to a field argument.

    Using `NonNull` will ensure that a value must be provided by the query
    '''
    def __init__(self, *args, **kwargs):
        as_container = kwargs.pop('_as_container', False)
        if as_container:
            # Is inited as container for the input args
            self.__init_container__(*args, **kwargs)
        else:
            # Is inited as UnmountedType, e.g.
            #
            # class MyObjectType(graphene.ObjectType):
            #     my_input = MyInputType(required=True)
            #
            UnmountedType.__init__(self, *args, **kwargs)

    def __init_container__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        for key, value in self.items():
            setattr(self, key, value)

    @classmethod
    def create_container(cls, data):
        return cls(data, _as_container=True)

    @classmethod
    def __init_subclass_with_meta__(cls, create_container=None, **options):
        _meta = InputObjectTypeOptions(cls)

        fields = OrderedDict()
        for base in reversed(cls.__mro__):
            fields.update(
                yank_fields_from_attrs(base.__dict__, _as=InputField)
            )

        _meta.fields = fields
        if create_container is None:
            create_container = cls.create_container
        _meta.create_container = create_container
        super(InputObjectType, cls).__init_subclass_with_meta__(_meta=_meta, **options)

    @classmethod
    def get_type(cls):
        '''
        This function is called when the unmounted type (InputObjectType instance)
        is mounted (as a Field, InputField or Argument)
        '''
        return cls
