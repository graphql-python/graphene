from functools import partial

import six

from ..utils.is_base_type import is_base_type
from ..utils.props import props
from .field import Field
from .objecttype import ObjectType, ObjectTypeMeta


class MutationMeta(ObjectTypeMeta):

    def __new__(cls, name, bases, attrs):
        super_new = super(MutationMeta, cls).__new__

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        if not is_base_type(bases, MutationMeta):
            return type.__new__(cls, name, bases, attrs)

        Input = attrs.pop('Input', None)

        cls = super_new(cls, name, bases, attrs)
        field_args = props(Input) if Input else {}
        resolver = getattr(cls, 'mutate', None)
        assert resolver, 'All mutations must define a mutate method in it'
        cls.Field = partial(Field, cls, args=field_args, resolver=resolver)
        return cls


class Mutation(six.with_metaclass(MutationMeta, ObjectType)):
    pass
