from ..utils.orderedtype import OrderedType
from .argument import Argument
from .field import Field, InputField


class UnmountedType(OrderedType):
    '''
    This class acts a proxy for a Graphene Type, so it can be mounted
    as Field, InputField or Argument.

    Instead of writing
    >>> class MyObjectType(ObjectType):
    >>>     my_field = Field(String(), description='Description here')

    It let you write
    >>> class MyObjectType(ObjectType):
    >>>     my_field = String(description='Description here')
    '''

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        super(UnmountedType, self).__init__()

    def get_type(self):
        return self._meta.graphql_type

    def as_field(self):
        '''
        Mount the UnmountedType as Field
        '''
        return Field(
            self.get_type(),
            *self.args,
            _creation_counter=self.creation_counter,
            **self.kwargs
        )

    def as_inputfield(self):
        '''
        Mount the UnmountedType as InputField
        '''
        return InputField(
            self.get_type(),
            *self.args,
            _creation_counter=self.creation_counter,
            **self.kwargs
        )

    def as_argument(self):
        '''
        Mount the UnmountedType as Argument
        '''
        return Argument(
            self.get_type(),
            *self.args,
            _creation_counter=self.creation_counter,
            **self.kwargs
        )
