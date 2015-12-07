import copy
import inspect
from collections import OrderedDict
from functools import partial

import six

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
            setattr(cls, 'NonNull', partial(NonNull, cls))
            setattr(cls, 'List', partial(List, cls))

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

    @property
    def fields_group_type(self):
        from ..types.field import FieldsGroupType
        return FieldsGroupType(*self.local_fields)


class FieldsClassTypeMeta(ClassTypeMeta):
    options_class = FieldsOptions

    def extend_fields(cls, bases):
        new_fields = cls._meta.local_fields
        field_names = {f.attname: f for f in new_fields}

        for base in bases:
            if not isinstance(base, FieldsClassTypeMeta):
                continue

            parent_fields = base._meta.local_fields
            for field in parent_fields:
                if field.attname in field_names and field.type.__class__ != field_names[
                        field.attname].type.__class__:
                    raise Exception(
                        'Local field %r in class %r (%r) clashes '
                        'with field with similar name from '
                        'Interface %s (%r)' % (
                            field.attname,
                            cls.__name__,
                            field.__class__,
                            base.__name__,
                            field_names[field.attname].__class__)
                    )
                new_field = copy.copy(field)
                cls.add_to_class(field.attname, new_field)

    def construct(cls, bases, attrs):
        cls = super(FieldsClassTypeMeta, cls).construct(bases, attrs)
        cls.extend_fields(bases)
        return cls


class FieldsClassType(six.with_metaclass(FieldsClassTypeMeta, ClassType)):

    class Meta:
        abstract = True

    @classmethod
    def fields_internal_types(cls, schema):
        return schema.T(cls._meta.fields_group_type)
