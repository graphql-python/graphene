import inspect

from ..utils.orderedtype import OrderedType


class Dynamic(OrderedType):
    '''
    A Dynamic Type let us get the type in runtime when we generate
    the schema. So we can have lazy fields.
    '''

    def __init__(self, type, _creation_counter=None):
        super(Dynamic, self).__init__(_creation_counter=_creation_counter)
        assert inspect.isfunction(type)
        self.type = type

    def get_type(self):
        return self.type()
