from functools import partial

import six

from ..utils.is_base_type import is_base_type
from ..utils.props import props
from .field import Field
from .objecttype import ObjectType, ObjectTypeMeta


class MutationMeta(ObjectTypeMeta):

    def __new__(cls, name, bases, attrs):
        # Also ensure initialization is only performed for subclasses of
        # Mutation
        if not is_base_type(bases, MutationMeta):
            return type.__new__(cls, name, bases, attrs)

        Input = attrs.pop('Input', None)

        cls = cls._create_objecttype(cls, name, bases, attrs)
        field_args = props(Input) if Input else {}
        resolver = getattr(cls, 'mutate', None)
        assert resolver, 'All mutations must define a mutate method in it'
        cls.Field = partial(Field, cls, args=field_args, resolver=resolver)
        return cls


class Mutation(six.with_metaclass(MutationMeta, ObjectType)):
    pass
