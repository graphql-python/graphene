from .field import Field
from .argument import Argument

from ..utils.orderedtype import OrderedType


class TypeProxy(OrderedType):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        OrderedType.__init__(self)

    def get_type(self):
        return self._meta.graphql_type

    def as_field(self):
        return Field(
            self.get_type(),
            *self.args,
            _creation_counter=self.creation_counter,
            **self.kwargs
        )

    def as_argument(self):
        return Argument(
            self.get_type(),
            *self.args,
            _creation_counter=self.creation_counter,
            **self.kwargs
        )

    def contribute_to_class(self, cls, attname):
        field = self.as_field()
        return field.contribute_to_class(cls, attname)
