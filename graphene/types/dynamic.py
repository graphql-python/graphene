import inspect

from ..utils.orderedtype import OrderedType


class Dynamic(OrderedType):

    def __init__(self, type, _creation_counter=None):
        super(Dynamic, self).__init__(_creation_counter=_creation_counter)
        assert inspect.isfunction(type)
        self.type = type

    def get_type(self):
        return self.type()
