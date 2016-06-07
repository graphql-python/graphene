from functools import partial
import six

from .objecttype import ObjectTypeMeta, ObjectType
from .field import Field

from ..utils.props import props


class MutationMeta(ObjectTypeMeta):

    def construct_field(cls, field_attrs):
        resolver = getattr(cls, 'mutate', None)
        assert resolver, 'All mutations must define a mutate method in it'
        return partial(Field, cls, args=field_attrs, resolver=resolver)

    def construct(cls, bases, attrs):
        super(MutationMeta, cls).construct(bases, attrs)
        if not cls._meta.abstract:
            Input = attrs.pop('Input', None)
            field_attrs = props(Input) if Input else {}
            cls.Field = cls.construct_field(field_attrs)
        return cls


class Mutation(six.with_metaclass(MutationMeta, ObjectType)):
    class Meta:
        abstract = True
