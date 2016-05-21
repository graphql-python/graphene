from ...core.exceptions import SkipField
from ...core.fields import Field
from ...core.types.base import FieldType
from ...core.types.definitions import List
from ...relay import ConnectionField
from ...relay.utils import is_node
from .utils import DJANGO_FILTER_INSTALLED, get_type_for_model, maybe_queryset


class DjangoConnectionField(ConnectionField):

    def __init__(self, *args, **kwargs):
        self.on = kwargs.pop('on', False)
        kwargs['default'] = kwargs.pop('default', self.get_manager)
        return super(DjangoConnectionField, self).__init__(*args, **kwargs)

    @property
    def model(self):
        return self.type._meta.model

    def get_manager(self):
        if self.on:
            return getattr(self.model, self.on)
        else:
            return self.model._default_manager

    def get_queryset(self, resolved_qs, args, info):
        return resolved_qs

    def from_list(self, connection_type, resolved, args, context, info):
        resolved_qs = maybe_queryset(resolved)
        qs = self.get_queryset(resolved_qs, args, info)
        return super(DjangoConnectionField, self).from_list(connection_type, qs, args, context, info)


class ConnectionOrListField(Field):

    def internal_type(self, schema):
        if DJANGO_FILTER_INSTALLED:
            from .filter.fields import DjangoFilterConnectionField

        model_field = self.type
        field_object_type = model_field.get_object_type(schema)
        if not field_object_type:
            raise SkipField()
        if is_node(field_object_type):
            if field_object_type._meta.filter_fields:
                field = DjangoFilterConnectionField(field_object_type)
            else:
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
