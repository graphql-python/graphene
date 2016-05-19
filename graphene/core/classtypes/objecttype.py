from functools import partial

import six
from graphql.type import GraphQLObjectType

from graphene import signals

from .base import FieldsClassType, FieldsClassTypeMeta, FieldsOptions
from .uniontype import UnionType


def is_objecttype(cls):
    if not issubclass(cls, ObjectType):
        return False
    return not(cls._meta.abstract or cls._meta.interface)


class ObjectTypeOptions(FieldsOptions):

    def __init__(self, *args, **kwargs):
        super(ObjectTypeOptions, self).__init__(*args, **kwargs)
        self.interface = False
        self.valid_attrs += ['interfaces']
        self.interfaces = []


class ObjectTypeMeta(FieldsClassTypeMeta):

    def construct(cls, bases, attrs):
        cls = super(ObjectTypeMeta, cls).construct(bases, attrs)
        if not cls._meta.abstract:
            union_types = list(filter(is_objecttype, bases))
            if len(union_types) > 1:
                meta_attrs = dict(cls._meta.original_attrs, types=union_types)
                Meta = type('Meta', (object, ), meta_attrs)
                attrs['Meta'] = Meta
                attrs['__module__'] = cls.__module__
                attrs['__doc__'] = cls.__doc__
                return type(cls.__name__, (UnionType, ), attrs)
        return cls

    options_class = ObjectTypeOptions


class ObjectType(six.with_metaclass(ObjectTypeMeta, FieldsClassType)):

    class Meta:
        abstract = True

    def __getattr__(self, name):
        if name == '_root':
            return
        return getattr(self._root, name)

    def __init__(self, *args, **kwargs):
        signals.pre_init.send(self.__class__, args=args, kwargs=kwargs)
        self._root = kwargs.pop('_root', None)
        args_len = len(args)
        fields = self._meta.fields
        if args_len > len(fields):
            # Daft, but matches old exception sans the err msg.
            raise IndexError("Number of args exceeds number of fields")
        fields_iter = iter(fields)

        if not kwargs:
            for val, field in zip(args, fields_iter):
                setattr(self, field.attname, val)
        else:
            for val, field in zip(args, fields_iter):
                setattr(self, field.attname, val)
                kwargs.pop(field.attname, None)

        for field in fields_iter:
            try:
                val = kwargs.pop(field.attname)
                setattr(self, field.attname, val)
            except KeyError:
                pass

        if kwargs:
            for prop in list(kwargs):
                try:
                    if isinstance(getattr(self.__class__, prop), property):
                        setattr(self, prop, kwargs.pop(prop))
                except AttributeError:
                    pass
            if kwargs:
                raise TypeError(
                    "'%s' is an invalid keyword argument for this function" %
                    list(kwargs)[0])

        signals.post_init.send(self.__class__, instance=self)

    @classmethod
    def internal_type(cls, schema):
        if cls._meta.abstract:
            raise Exception("Abstract ObjectTypes don't have a specific type.")

        return GraphQLObjectType(
            cls._meta.type_name,
            description=cls._meta.description,
            interfaces=list(map(schema.T, cls._meta.interfaces)),
            fields=partial(cls.fields_internal_types, schema),
            is_type_of=getattr(cls, 'is_type_of', None)
        )

    @classmethod
    def wrap(cls, instance, args, info):
        return cls(_root=instance)
