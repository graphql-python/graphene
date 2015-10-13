import inspect
import six
import copy
from collections import OrderedDict

from graphql.core.type import (
    GraphQLObjectType,
    GraphQLInterfaceType
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
        return Mutation in parents

    def __new__(cls, name, bases, attrs):
        super_new = super(ObjectTypeMeta, cls).__new__
        parents = [b for b in bases if isinstance(b, cls)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return super_new(cls, name, bases, attrs)

        module = attrs.pop('__module__')
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

        new_class._meta.interface = new_class.is_interface(parents)
        new_class._meta.mutation = new_class.is_mutation(parents)

        assert not (new_class._meta.interface and new_class._meta.mutation)

        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)
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
                        'Local field %r in class %r clashes '
                        'with field with similar name from '
                        'Interface %s (%r != %r)' % (
                            field.name,
                            new_class.__name__,
                            base.__name__,
                            field.__class__,
                            field_names[field.name].__class__)
                    )
                new_field = copy.copy(field)
                new_class.add_to_class(field.field_name, new_field)

            new_class._meta.parents.append(base)
            if base._meta.interface:
                new_class._meta.interfaces.append(base)
            # new_class._meta.parents.extend(base._meta.parents)

        new_class._prepare()
        return new_class

    def add_extra_fields(cls):
        pass

    def _prepare(cls):
        signals.class_prepared.send(cls)

    def add_to_class(cls, name, value):
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class BaseObjectType(object):

    def __new__(cls, instance=None, *args, **kwargs):
        if cls._meta.interface:
            raise Exception("An interface cannot be initialized")
        if instance is None:
            return None
        elif type(instance) is cls:
            instance = instance.instance
        return super(BaseObjectType, cls).__new__(cls, *args, **kwargs)

    def __init__(self, instance):
        signals.pre_init.send(self.__class__, instance=instance)
        self.instance = instance
        signals.post_init.send(self.__class__, instance=self)

    def __getattr__(self, name):
        if self.instance:
            return getattr(self.instance, name)

    def get_field(self, field):
        return getattr(self.instance, field, None)

    def resolve(self, field_name, args, info):
        custom_resolve_fn = 'resolve_%s' % field_name
        if hasattr(self, custom_resolve_fn):
            resolve_fn = getattr(self, custom_resolve_fn)
            return resolve_fn(args, info)
        return self.get_field(field_name)

    @classmethod
    def resolve_type(cls, schema, instance, *_):
        return instance.internal_type(schema)

    @classmethod
    @memoize
    @register_internal_type
    def internal_type(cls, schema):
        fields_list = cls._meta.fields
        fields = lambda: OrderedDict([(f.name, f.internal_field(schema))
                                      for f in fields_list])
        if cls._meta.interface:
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
            fields=fields
        )


class ObjectType(six.with_metaclass(ObjectTypeMeta, BaseObjectType)):
    pass


class Mutation(six.with_metaclass(ObjectTypeMeta, BaseObjectType)):
    pass


class Interface(six.with_metaclass(ObjectTypeMeta, BaseObjectType)):
    pass
