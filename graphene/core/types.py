import inspect
import six

from graphql.core.type import (
    GraphQLObjectType,
    GraphQLInterfaceType,
    GraphQLSchema
)
from graphql.core import graphql

from graphene import signals
from graphene.core.options import Options


class ObjectTypeMeta(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(ObjectTypeMeta, cls).__new__
        parents = [b for b in bases if isinstance(b, ObjectTypeMeta)]
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
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta
        base_meta = getattr(new_class, '_meta', None)

        if '.' in module:
            app_label, _ = module.rsplit('.', 1)
        else:
            app_label = module

        new_class.add_to_class('_meta', Options(meta, app_label))
        if base_meta and base_meta.proxy:
            new_class._meta.interface = base_meta.interface
        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            new_class.add_to_class(obj_name, obj)

        new_fields = new_class._meta.local_fields
        field_names = {f.field_name for f in new_fields}

        for base in parents:
            original_base = base
            if not hasattr(base, '_meta'):
                # Things without _meta aren't functional models, so they're
                # uninteresting parents.
                continue

            parent_fields = base._meta.local_fields
            # Check for clashes between locally declared fields and those
            # on the base classes (we cannot handle shadowed fields at the
            # moment).
            for field in parent_fields:
                if field.field_name in field_names:
                    raise Exception(
                        'Local field %r in class %r clashes '
                        'with field of similar name from '
                        'base class %r' % (field.field_name, name, base.__name__)
                    )
            new_class._meta.parents.append(base)
            if base._meta.interface:
                new_class._meta.interfaces.append(base)
            # new_class._meta.parents.extend(base._meta.parents)

        new_class._prepare()
        return new_class

    def _prepare(cls):
        signals.class_prepared.send(cls)

    def add_to_class(cls, name, value):
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class ObjectType(six.with_metaclass(ObjectTypeMeta)):
    def __init__(self, instance=None):
        signals.pre_init.send(self.__class__, instance=instance)
        self.instance = instance
        signals.post_init.send(self.__class__, instance=self)

    def get_field(self, field):
        return getattr(self.instance, field, None)

    def resolve(self, field_name, args, info):
        if field_name not in self._meta.fields_map.keys():
            raise Exception('Field %s not found in model' % field_name)
        custom_resolve_fn = 'resolve_%s' % field_name
        if hasattr(self, custom_resolve_fn):
            resolve_fn = getattr(self, custom_resolve_fn)
            return resolve_fn(args, info)
        return self.get_field(field_name)

    @classmethod
    def can_resolve(cls, field_name, instance, args, info):
        # Useful for manage permissions in fields
        return True

    @classmethod
    def resolve_type(cls, instance, *_):
        return instance._meta.type

    @classmethod
    def get_graphql_type(cls):
        fields = cls._meta.fields_map
        if cls._meta.interface:
            return GraphQLInterfaceType(
                cls._meta.type_name,
                description=cls._meta.description,
                resolve_type=cls.resolve_type,
                fields=lambda: {name: field.field for name, field in fields.items()}
            )
        return GraphQLObjectType(
            cls._meta.type_name,
            description=cls._meta.description,
            interfaces=[i._meta.type for i in cls._meta.interfaces],
            fields=lambda: {name: field.field for name, field in fields.items()}
        )


class Interface(ObjectType):
    class Meta:
        interface = True
        proxy = True


class Schema(object):
    def __init__(self, query, mutation=None):
        self.query = query
        self.query_type = query._meta.type
        self._schema = GraphQLSchema(query=self.query_type, mutation=mutation)

    def execute(self, request='', root=None, vars=None, operation_name=None):
        return graphql(
            self._schema,
            request=request,
            root=root or self.query(),
            vars=vars,
            operation_name=operation_name
        )
