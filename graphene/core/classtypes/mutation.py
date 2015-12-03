import six

from .objecttype import ObjectType, ObjectTypeMeta


class MutationMeta(ObjectTypeMeta):

    def construct(cls, bases, attrs):
        input_class = attrs.pop('Input', None)
        if input_class:
            items = dict(vars(input_class))
            items.pop('__dict__', None)
            items.pop('__doc__', None)
            items.pop('__module__', None)
            items.pop('__weakref__', None)
            cls.add_to_class('arguments', cls.construct_arguments(items))
        cls = super(MutationMeta, cls).construct(bases, attrs)
        return cls

    def construct_arguments(cls, items):
        from ..types.argument import ArgumentsGroup
        return ArgumentsGroup(**items)


class Mutation(six.with_metaclass(MutationMeta, ObjectType)):

    class Meta:
        abstract = True

    @classmethod
    def get_arguments(cls):
        return cls.arguments
