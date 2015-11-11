from functools import total_ordering


class BaseType(object):
    @classmethod
    def internal_type(cls, schema):
        return getattr(cls, 'T', None)


class LazyType(BaseType):
    def __init__(self, type_str):
        self.type_str = type_str

    def is_self(self):
        return self.type_str == 'self'

    def internal_type(self, schema):
        type = schema.get_type(self.type_str)
        return schema.T(type)


@total_ordering
class OrderedType(BaseType):
    creation_counter = 0

    def __init__(self, _creation_counter=None):
        self.creation_counter = _creation_counter or self.gen_counter()

    @staticmethod
    def gen_counter():
        counter = OrderedType.creation_counter
        OrderedType.creation_counter += 1
        return counter

    def __eq__(self, other):
        # Needed for @total_ordering
        if type(self) == type(other):
            return self.creation_counter == other.creation_counter
        return NotImplemented

    def __lt__(self, other):
        # This is needed because bisect does not take a comparison function.
        if type(self) == type(other):
            return self.creation_counter < other.creation_counter
        return NotImplemented

    def __hash__(self):
        return hash((self.creation_counter))


class MirroredType(OrderedType):
    def __init__(self, *args, **kwargs):
        _creation_counter = kwargs.pop('_creation_counter', None)
        super(MirroredType, self).__init__(_creation_counter=_creation_counter)
        self.args = args
        self.kwargs = kwargs


class ArgumentType(MirroredType):
    def as_argument(self):
        from .argument import Argument
        return Argument(self, _creation_counter=self.creation_counter, *self.args, **self.kwargs)


class FieldType(MirroredType):
    def contribute_to_class(self, cls, name):
        from ..types import BaseObjectType, InputObjectType
        if issubclass(cls, InputObjectType):
            inputfield = self.as_inputfield()
            return inputfield.contribute_to_class(cls, name)
        elif issubclass(cls, BaseObjectType):
            field = self.as_field()
            return field.contribute_to_class(cls, name)

    def as_field(self):
        from .field import Field
        return Field(self, _creation_counter=self.creation_counter, *self.args, **self.kwargs)

    def as_inputfield(self):
        from .field import InputField
        return InputField(self, _creation_counter=self.creation_counter, *self.args, **self.kwargs)


class MountedType(FieldType, ArgumentType):
    pass
