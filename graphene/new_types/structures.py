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
    def __str__(self):
        return '[{}]'.format(self.of_type)


class NonNull(Structure):
    def __str__(self):
        return '{}!'.format(self.of_type)
