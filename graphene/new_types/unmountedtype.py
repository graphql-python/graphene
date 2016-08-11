from ..utils.orderedtype import OrderedType
# from .argument import Argument



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
        super(UnmountedType, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def get_type(self):
        raise NotImplementedError("get_type not implemented in {}".format(self))

    def as_field(self):
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

    # def as_inputfield(self):
    #     '''
    #     Mount the UnmountedType as InputField
    #     '''
    #     return InputField(
    #         self.get_type(),
    #         *self.args,
    #         _creation_counter=self.creation_counter,
    #         **self.kwargs
    #     )

    # def as_argument(self):
    #     '''
    #     Mount the UnmountedType as Argument
    #     '''
    #     return Argument(
    #         self.get_type(),
    #         *self.args,
    #         _creation_counter=self.creation_counter,
    #         **self.kwargs
    #     )
