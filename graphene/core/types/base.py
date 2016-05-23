from collections import OrderedDict
from functools import partial, total_ordering

import six

from ...utils import to_camel_case


class InstanceType(object):

    def internal_type(self, schema):
        raise NotImplementedError("internal_type for type {} is not implemented".format(self.__class__.__name__))


class MountType(InstanceType):
    parent = None

    def mount(self, cls):
        self.parent = cls


class LazyType(MountType):

    def __init__(self, type):
        self.type = type

    @property
    def is_self(self):
        return self.type == 'self'

    def internal_type(self, schema):
        type = None
        if callable(self.type):
            type = self.type(self.parent)
        elif isinstance(self.type, six.string_types):
            if self.is_self:
                type = self.parent
            else:
                type = schema.get_type(self.type)
        assert type, 'Type in %s %r cannot be none' % (self.type, self.parent)
        return schema.T(type)


@total_ordering
class OrderedType(MountType):
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
        if isinstance(self, type(other)):
            return self.creation_counter == other.creation_counter
        return NotImplemented

    def __lt__(self, other):
        # This is needed because bisect does not take a comparison function.
        if isinstance(other, OrderedType):
            return self.creation_counter < other.creation_counter
        return NotImplemented

    def __gt__(self, other):
        # This is needed because bisect does not take a comparison function.
        if isinstance(other, OrderedType):
            return self.creation_counter > other.creation_counter
        return NotImplemented

    def __hash__(self):
        return hash((self.creation_counter))


class MirroredType(OrderedType):

    def __init__(self, *args, **kwargs):
        _creation_counter = kwargs.pop('_creation_counter', None)
        super(MirroredType, self).__init__(_creation_counter=_creation_counter)
        self.args = args
        self.kwargs = kwargs

    @property
    def List(self):  # noqa
        from .definitions import List
        return List(self, *self.args, **self.kwargs)

    @property
    def NonNull(self):  # noqa
        from .definitions import NonNull
        return NonNull(self, *self.args, **self.kwargs)


class ArgumentType(MirroredType):

    def as_argument(self):
        from .argument import Argument
        return Argument(
            self, _creation_counter=self.creation_counter, *self.args, **self.kwargs)


class FieldType(MirroredType):

    def contribute_to_class(self, cls, name):
        from ..classtypes.base import FieldsClassType
        from ..classtypes.inputobjecttype import InputObjectType
        if issubclass(cls, (InputObjectType)):
            inputfield = self.as_inputfield()
            return inputfield.contribute_to_class(cls, name)
        elif issubclass(cls, (FieldsClassType)):
            field = self.as_field()
            return field.contribute_to_class(cls, name)

    def as_field(self):
        from .field import Field
        return Field(self, _creation_counter=self.creation_counter,
                     *self.args, **self.kwargs)

    def as_inputfield(self):
        from .field import InputField
        return InputField(
            self, _creation_counter=self.creation_counter, *self.args, **self.kwargs)


class MountedType(FieldType, ArgumentType):
    pass


class NamedType(InstanceType):

    def __init__(self, name=None, default_name=None, *args, **kwargs):
        self.name = name
        self.default_name = None
        super(NamedType, self).__init__(*args, **kwargs)


class GroupNamedType(InstanceType):

    def __init__(self, *types):
        self.types = types

    def get_named_type(self, schema, type):
        name = type.name
        if not name and schema.auto_camelcase:
            name = to_camel_case(type.default_name)
        elif not name:
            name = type.default_name
        return name, schema.T(type)

    def iter_types(self, schema):
        return map(partial(self.get_named_type, schema), self.types)

    def internal_type(self, schema):
        return OrderedDict(self.iter_types(schema))

    def __len__(self):
        return len(self.types)

    def __iter__(self):
        return iter(self.types)

    def __contains__(self, *args):
        return self.types.__contains__(*args)

    def __getitem__(self, *args):
        return self.types.__getitem__(*args)
