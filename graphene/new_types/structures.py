from .unmountedtype import UnmountedType


class Structure(UnmountedType):
    '''
    A structure is a GraphQL type instance that
    wraps a main type with certain structure.
    '''

    def __init__(self, of_type, *args, **kwargs):
        super(Structure, self).__init__(*args, **kwargs)
        self.of_type = of_type

    def get_type(self):
        return self


class List(Structure):
    pass


class NonNull(Structure):
    pass
