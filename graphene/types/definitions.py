from collections import OrderedDict
import inspect
from itertools import chain
from functools import partial

from graphql.utils.assert_valid_name import assert_valid_name

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

        new_class._meta = new_class.get_options(meta)
        new_class._meta.parent = new_class
        new_class._meta.validate_attrs()

        if new_class._meta.name:
            assert_valid_name(new_class._meta.name)

        return mcs.construct(new_class, bases, attrs)

    def get_options(cls, meta):
        raise NotImplementedError("get_options is not implemented")

    def construct(cls, bases, attrs):
        # Add all attributes to the class.
        for name, value in attrs.items():
            setattr(cls, name, value)

        return cls


class FieldsMeta(type):

    def _build_field_map(cls, bases, local_fields):
        from ..utils.extract_fields import get_base_fields
        extended_fields = list(get_base_fields(cls, bases))

        fields = []
        field_names = set(f.name for f in local_fields)
        for extended_field in extended_fields:
            if extended_field.name in field_names:
                continue
            fields.append(extended_field)
            field_names.add(extended_field.name)

        fields.extend(local_fields)

        return OrderedDict((f.name, f) for f in fields)

    def _extract_local_fields(cls, attrs):
        from ..utils.extract_fields import extract_fields
        return extract_fields(cls, attrs)

    def _fields(cls, bases, attrs, local_fields, extra_types=()):
        from ..utils.is_graphene_type import is_graphene_type
        inherited_types = tuple(
            base._meta.graphql_type for base in bases if is_graphene_type(base) and not base._meta.abstract
        ) + extra_types
        return partial(cls._build_field_map, inherited_types, local_fields)


class GrapheneGraphQLType(object):
    def __init__(self, *args, **kwargs):
        self.graphene_type = kwargs.pop('graphene_type')
        super(GrapheneGraphQLType, self).__init__(*args, **kwargs)
