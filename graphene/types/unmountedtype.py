from ..utils.orderedtype import OrderedType


class UnmountedType(OrderedType):
    '''
    This class acts a proxy for a Graphene Type, so it can be mounted
    dynamically as Field, InputField or Argument.

    Instead of writing
    >>> class MyObjectType(ObjectType):
    >>>     my_field = Field(String(), description='Description here')

    It let you write
    >>> class MyObjectType(ObjectType):
    >>>     my_field = String(description='Description here')
    '''

    def __init__(self, *args, **kwargs):
        super(UnmountedType, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def get_type(self):
        raise NotImplementedError("get_type not implemented in {}".format(self))

    def Field(self):  # noqa: N802
        '''
        Mount the UnmountedType as Field
        '''
        from .field import Field
        return Field(
            self.get_type(),
            *self.args,
            _creation_counter=self.creation_counter,
            **self.kwargs
        )

    def InputField(self):  # noqa: N802
        '''
        Mount the UnmountedType as InputField
        '''
        from .inputfield import InputField
        return InputField(
            self.get_type(),
            *self.args,
            _creation_counter=self.creation_counter,
            **self.kwargs
        )

    def Argument(self):  # noqa: N802
        '''
        Mount the UnmountedType as Argument
        '''
        from .argument import Argument
        return Argument(
            self.get_type(),
            *self.args,
            _creation_counter=self.creation_counter,
            **self.kwargs
        )

    def __eq__(self, other):
        return (
            self is other or (
                isinstance(other, UnmountedType) and
                self.get_type() == other.get_type() and
                self.args == other.args and
                self.kwargs == other.kwargs
            )
        )
