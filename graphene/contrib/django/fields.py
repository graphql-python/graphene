import warnings

from graphene.contrib.django.utils import get_filtering_args_from_filterset
from .resolvers import FilterConnectionResolver
from .utils import get_type_for_model
from ...core.exceptions import SkipField
from ...core.fields import Field
from ...core.types.base import FieldType
from ...core.types.definitions import List
from ...relay import ConnectionField
from ...relay.utils import is_node


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

    def __init__(self, type, on=None, fields=None, order_by=None,
                 extra_filter_meta=None, filterset_class=None, resolver=None,
                 *args, **kwargs):

        if not resolver:
            resolver = FilterConnectionResolver(
                node=type,
                on=on,
                filterset_class=filterset_class,
                fields=fields,
                order_by=order_by,
                extra_filter_meta=extra_filter_meta,
            )

        filtering_args = get_filtering_args_from_filterset(resolver.get_filterset_class(), type)
        kwargs.setdefault('args', {})
        kwargs['args'].update(**filtering_args)
        super(DjangoFilterConnectionField, self).__init__(type, resolver, *args, **kwargs)
