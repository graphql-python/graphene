from functools import partial

import six

from ..utils.is_base_type import is_base_type
from ..utils.get_unbound_function import get_unbound_function
from ..utils.props import props
from .field import Field
from .objecttype import ObjectType, ObjectTypeMeta


class MutationMeta(ObjectTypeMeta):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # Mutation
        if not is_base_type(bases, MutationMeta):
            return type.__new__(cls, name, bases, attrs)

        input_class = attrs.pop('Input', None)

        cls = ObjectTypeMeta.__new__(cls, name, bases, attrs)
        field_args = props(input_class) if input_class else {}
        resolver = getattr(cls, 'mutate', None)
        assert resolver, 'All mutations must define a mutate method in it'
        resolver = get_unbound_function(resolver)
        cls.Field = partial(Field, cls, args=field_args, resolver=resolver)
        return cls


class Mutation(six.with_metaclass(MutationMeta, ObjectType)):
    pass
