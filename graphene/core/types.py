import inspect
import six
import copy
from collections import OrderedDict

from graphql.core.type import (
    GraphQLObjectType,
    GraphQLInputObjectType,
    GraphQLInterfaceType,
    GraphQLArgument
)

from graphene import signals
from graphene.core.options import Options
from graphene.utils import memoize
from graphene.core.schema import register_internal_type


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

        base_meta = getattr(new_class, '_meta', None)

        new_class.add_to_class('_meta', new_class.options_cls(meta))

        new_class._meta.is_interface = new_class.is_interface(parents)
        new_class._meta.is_mutation = new_class.is_mutation(parents)

        assert not (new_class._meta.is_interface and new_class._meta.is_mutation)

        input_class = None
        if new_class._meta.is_mutation:
            input_class = attrs.pop('Input', None)

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        if new_class._meta.is_mutation:
            assert hasattr(new_class, 'mutate'), "All mutations must implement mutate method"

        if input_class:
            items = dict(input_class.__dict__)
            items.pop('__dict__', None)
            input_type = type('{}Input'.format(new_class._meta.type_name), (ObjectType, ), items)
            new_class.add_to_class('input_type', input_type)

        new_class.add_extra_fields()

        new_fields = new_class._meta.local_fields
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
                if field.name in field_names and field.__class__ != field_names[field.name].__class__:
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
                new_class.add_to_class(field.field_name, new_field)

            new_class._meta.parents.append(base)
            if base._meta.is_interface:
                new_class._meta.interfaces.append(base)
            # new_class._meta.parents.extend(base._meta.parents)

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
        if not inspect.isclass(value) and hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class BaseObjectType(object):

    def __new__(cls, *args, **kwargs):
        if cls._meta.is_interface:
            raise Exception("An interface cannot be initialized")
        if not args and not kwargs:
            return None
        return super(BaseObjectType, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        signals.pre_init.send(self.__class__, args=args, kwargs=kwargs)
        args_len = len(args)
        fields = self._meta.fields
        if args_len > len(fields):
            # Daft, but matches old exception sans the err msg.
            raise IndexError("Number of args exceeds number of fields")
        fields_iter = iter(fields)

        if not kwargs:
            for val, field in zip(args, fields_iter):
                setattr(self, field.field_name, val)
        else:
            for val, field in zip(args, fields_iter):
                setattr(self, field.field_name, val)
                kwargs.pop(field.field_name, None)

        for field in fields_iter:
            try:
                val = kwargs.pop(field.field_name)
                setattr(self, field.field_name, val)
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
                raise TypeError("'%s' is an invalid keyword argument for this function" % list(kwargs)[0])

        signals.post_init.send(self.__class__, instance=self)

    @classmethod
    def fields_as_arguments(cls, schema):
        return OrderedDict([(f.field_name, GraphQLArgument(f.internal_type(schema)))
                            for f in cls._meta.fields])

    @classmethod
    def resolve_objecttype(cls, schema, instance, *_):
        return instance

    @classmethod
    def resolve_type(cls, schema, instance, *_):
        objecttype = cls.resolve_objecttype(schema, instance, *_)
        return objecttype.internal_type(schema)

    @classmethod
    @memoize
    @register_internal_type
    def internal_type(cls, schema):
        fields = lambda: OrderedDict([(f.name, f.internal_field(schema))
                                      for f in cls._meta.fields])
        if cls._meta.is_interface:
            return GraphQLInterfaceType(
                cls._meta.type_name,
                description=cls._meta.description,
                resolve_type=lambda *
                args, **kwargs: cls.resolve_type(schema, *args, **kwargs),
                fields=fields
            )
        return GraphQLObjectType(
            cls._meta.type_name,
            description=cls._meta.description,
            interfaces=[i.internal_type(schema) for i in cls._meta.interfaces],
            fields=fields,
            is_type_of=getattr(cls, 'is_type_of', None)
        )


class Interface(six.with_metaclass(ObjectTypeMeta, BaseObjectType)):
    pass


class ObjectType(six.with_metaclass(ObjectTypeMeta, BaseObjectType)):
    pass


class Mutation(six.with_metaclass(ObjectTypeMeta, BaseObjectType)):
    @classmethod
    def get_input_type(cls):
        return getattr(cls, 'input_type', None)


class InputObjectType(ObjectType):
    @classmethod
    @memoize
    @register_internal_type
    def internal_type(cls, schema):
        fields = lambda: OrderedDict([(f.name, f.internal_field(schema))
                                      for f in cls._meta.fields])
        return GraphQLInputObjectType(
            cls._meta.type_name,
            description=cls._meta.description,
            fields=fields,
        )
