import warnings

import six

from graphene.contrib.django.filterset import setup_filterset
from ...core.exceptions import SkipField
from ...core.fields import Field
from ...core.types import Argument, String
from ...core.types.base import FieldType
from ...core.types.definitions import List
from ...relay import ConnectionField
from ...relay.utils import is_node
from .form_converter import convert_form_field
from .resolvers import FilterConnectionResolver
from .utils import get_type_for_model
from .filterset import custom_filterset_factory


class DjangoConnectionField(ConnectionField):

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        warnings.warn("Using {} will be not longer supported."
                      " Use relay.ConnectionField instead".format(cls.__name__),
                      FutureWarning)
        return super(DjangoConnectionField, self).__init__(*args, **kwargs)


class ConnectionOrListField(Field):

    def internal_type(self, schema):
        model_field = self.type
        field_object_type = model_field.get_object_type(schema)
        if not field_object_type:
            raise SkipField()
        if is_node(field_object_type):
            field = DjangoConnectionField(field_object_type)
        else:
            field = Field(List(field_object_type))
        field.contribute_to_class(self.object_type, self.attname)
        return schema.T(field)


class DjangoModelField(FieldType):

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(DjangoModelField, self).__init__(*args, **kwargs)

    def internal_type(self, schema):
        _type = self.get_object_type(schema)
        if not _type and self.parent._meta.only_fields:
            raise Exception(
                "Model %r is not accessible by the schema. "
                "You can either register the type manually "
                "using @schema.register. "
                "Or disable the field in %s" % (
                    self.model,
                    self.parent,
                )
            )
        if not _type:
            raise SkipField()
        return schema.T(_type)

    def get_object_type(self, schema):
        return get_type_for_model(schema, self.model)


class DjangoFilterConnectionField(DjangoConnectionField):

    def __init__(self, type, filterset_class=None, resolver=None, on=None,
                 fields=None, order_by=None, extra_filter_meta=None,
                 *args, **kwargs):

        if not filterset_class:
            # If no filter class is specified then create one given the
            # information provided
            meta = dict(
                model=type._meta.model,
                fields=fields,
                order_by=order_by,
            )
            if extra_filter_meta:
                meta.update(extra_filter_meta)
            filterset_class = custom_filterset_factory(**meta)
        else:
            filterset_class = setup_filterset(filterset_class)

        if not resolver:
            resolver = FilterConnectionResolver(type, on, filterset_class)

        kwargs.setdefault('args', {})
        kwargs['args'].update(**self.get_filtering_args(type, filterset_class))
        super(DjangoFilterConnectionField, self).__init__(type, resolver, *args, **kwargs)

    def get_filtering_args(self, type, filterset_class):
        args = {}
        for name, filter_field in six.iteritems(filterset_class.base_filters):
            field_type = Argument(convert_form_field(filter_field.field))
            # Is this correct? I don't quite grok the 'parent' system yet
            field_type.mount(type)
            args[name] = field_type

        # Also add the 'order_by' field
        args[filterset_class.order_by_field] = Argument(String)
        return args
