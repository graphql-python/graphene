import copy
import inspect
from collections import OrderedDict
from functools import partial

import six
from graphql.core.type import (GraphQLInputObjectType, GraphQLInterfaceType,
                               GraphQLObjectType, GraphQLUnionType)

from graphene import signals

from ..exceptions import SkipField
from ..options import Options
from .argument import ArgumentsGroup
from .base import BaseType
from .definitions import List, NonNull


class ObjectTypeMeta(type):
    options_cls = Options

    def is_interface(cls, parents):
        return Interface in parents

    def is_mutation(cls, parents):
        return issubclass(cls, Mutation)

    def __new__(cls, name, bases, attrs):
        super_new = super(ObjectTypeMeta, cls).__new__
        parents = [b for b in bases if isinstance(b, cls)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return super_new(cls, name, bases, attrs)

        module = attrs.pop('__module__', None)
        doc = attrs.pop('__doc__', None)
        new_class = super_new(cls, name, bases, {
            '__module__': module,
            '__doc__': doc
        })
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = None
            # meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta

        getattr(new_class, '_meta', None)

        new_class.add_to_class('_meta', new_class.options_cls(meta))

        new_class._meta.is_interface = new_class.is_interface(parents)
        new_class._meta.is_mutation = new_class.is_mutation(parents)
        union_types = [p for p in parents if issubclass(p, BaseObjectType)]

        new_class._meta.is_union = len(union_types) > 1
        new_class._meta.types = union_types

        assert not (
            new_class._meta.is_interface and new_class._meta.is_mutation)

        assert not (
            new_class._meta.is_interface and new_class._meta.is_union)

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        if new_class._meta.is_mutation:
            assert hasattr(
                new_class, 'mutate'), "All mutations must implement mutate method"

        new_class.add_extra_fields()

        new_fields = new_class._meta.local_fields
        assert not(new_class._meta.is_union and new_fields), 'An union cannot have extra fields'

        field_names = {f.name: f for f in new_fields}

        for base in parents:
            if not hasattr(base, '_meta'):
                # Things without _meta aren't functional models, so they're
                # uninteresting parents.
                continue
            # if base._meta.schema != new_class._meta.schema:
            #     raise Exception('The parent schema is not the same')

            parent_fields = base._meta.local_fields
            # Check for clashes between locally declared fields and those
            # on the base classes (we cannot handle shadowed fields at the
            # moment).
            for field in parent_fields:
                if field.name in field_names and field.type.__class__ != field_names[
                        field.name].type.__class__:
                    raise Exception(
                        'Local field %r in class %r (%r) clashes '
                        'with field with similar name from '
                        'Interface %s (%r)' % (
                            field.name,
                            new_class.__name__,
                            field.__class__,
                            base.__name__,
                            field_names[field.name].__class__)
                    )
                new_field = copy.copy(field)
                new_class.add_to_class(field.attname, new_field)

            new_class._meta.parents.append(base)
            if base._meta.is_interface:
                new_class._meta.interfaces.append(base)
            # new_class._meta.parents.extend(base._meta.parents)

        setattr(new_class, 'NonNull', NonNull(new_class))
        setattr(new_class, 'List', List(new_class))

        new_class._prepare()
        return new_class

    def add_extra_fields(cls):
        pass

    def _prepare(cls):
        if hasattr(cls, '_prepare_class'):
            cls._prepare_class()
        signals.class_prepared.send(cls)

    def add_to_class(cls, name, value):
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and hasattr(
                value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class BaseObjectType(BaseType):

    def __new__(cls, *args, **kwargs):
        if cls._meta.is_interface:
            raise Exception("An interface cannot be initialized")
        if cls._meta.is_union:
            raise Exception("An union cannot be initialized")
        return super(BaseObjectType, cls).__new__(cls)

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
    def resolve_type(cls, schema, instance, *args):
        return schema.T(instance.__class__)

    @classmethod
    def internal_type(cls, schema):
        if cls._meta.is_interface:
            return GraphQLInterfaceType(
                cls._meta.type_name,
                description=cls._meta.description,
                resolve_type=partial(cls.resolve_type, schema),
                fields=partial(cls.get_fields, schema)
            )
        elif cls._meta.is_union:
            return GraphQLUnionType(
                cls._meta.type_name,
                types=cls._meta.types,
                description=cls._meta.description,
            )
        return GraphQLObjectType(
            cls._meta.type_name,
            description=cls._meta.description,
            interfaces=[schema.T(i) for i in cls._meta.interfaces],
            fields=partial(cls.get_fields, schema),
            is_type_of=getattr(cls, 'is_type_of', None)
        )

    @classmethod
    def get_fields(cls, schema):
        fields = []
        for field in cls._meta.fields:
            try:
                fields.append((field.name, schema.T(field)))
            except SkipField:
                continue

        return OrderedDict(fields)


class Interface(six.with_metaclass(ObjectTypeMeta, BaseObjectType)):
    pass


class ObjectType(six.with_metaclass(ObjectTypeMeta, BaseObjectType)):
    pass


class Mutation(six.with_metaclass(ObjectTypeMeta, BaseObjectType)):

    @classmethod
    def _construct_arguments(cls, items):
        return ArgumentsGroup(**items)

    @classmethod
    def _prepare_class(cls):
        input_class = getattr(cls, 'Input', None)
        if input_class:
            items = dict(vars(input_class))
            items.pop('__dict__', None)
            items.pop('__doc__', None)
            items.pop('__module__', None)
            items.pop('__weakref__', None)
            cls.add_to_class('arguments', cls._construct_arguments(items))
            delattr(cls, 'Input')

    @classmethod
    def get_arguments(cls):
        return cls.arguments


class InputObjectType(ObjectType):

    @classmethod
    def internal_type(cls, schema):
        return GraphQLInputObjectType(
            cls._meta.type_name,
            description=cls._meta.description,
            fields=partial(cls.get_fields, schema),
        )
