from collections import OrderedDict
import inspect
import six

from ..exceptions import SkipField
from .options import Options


class ClassTypeMeta(type):
    options_class = Options

    def __new__(mcs, name, bases, attrs):
        super_new = super(ClassTypeMeta, mcs).__new__

        module = attrs.pop('__module__', None)
        doc = attrs.pop('__doc__', None)
        new_class = super_new(mcs, name, bases, {
            '__module__': module,
            '__doc__': doc
        })
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta

        new_class.add_to_class('_meta', new_class.get_options(meta))

        return mcs.construct(new_class, bases, attrs)

    def get_options(cls, meta):
        return cls.options_class(meta)

    def add_to_class(cls, name, value):
        # We should call the contribute_to_class method only if it's bound
        if not inspect.isclass(value) and hasattr(
                value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)

    def construct(cls, bases, attrs):
        # Add all attributes to the class.
        for obj_name, obj in attrs.items():
            cls.add_to_class(obj_name, obj)

        if not cls._meta.abstract:
            from ..types import List, NonNull
            setattr(cls, 'NonNull', NonNull(cls))
            setattr(cls, 'List', List(cls))

        return cls


class ClassType(six.with_metaclass(ClassTypeMeta)):
    class Meta:
        abstract = True

    @classmethod
    def internal_type(cls, schema):
        raise NotImplementedError("Function internal_type not implemented in type {}".format(cls))


class FieldsOptions(Options):
    def __init__(self, *args, **kwargs):
        super(FieldsOptions, self).__init__(*args, **kwargs)
        self.local_fields = []

    def add_field(self, field):
        self.local_fields.append(field)

    @property
    def fields(self):
        return sorted(self.local_fields)

    @property
    def fields_map(self):
        return OrderedDict([(f.attname, f) for f in self.fields])


class FieldsClassTypeMeta(ClassTypeMeta):
    options_class = FieldsOptions


class FieldsClassType(six.with_metaclass(FieldsClassTypeMeta, ClassType)):
    class Meta:
        abstract = True

    @classmethod
    def fields_internal_types(cls, schema):
        fields = []
        for field in cls._meta.fields:
            try:
                fields.append((field.name, schema.T(field)))
            except SkipField:
                continue

        return OrderedDict(fields)

# class NamedClassType(ClassType):
#     pass


# class UnionType(NamedClassType):
#     class Meta:
#         abstract = True


# class ObjectType(NamedClassType):
#     class Meta:
#         abstract = True


# class InputObjectType(NamedClassType):
#     class Meta:
#         abstract = True


# class Mutation(ObjectType):
#     class Meta:
#         abstract = True
