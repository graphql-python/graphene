from ...core.exceptions import SkipField
from ...core.fields import Field
from ...core.types.base import FieldType
from ...core.types.definitions import List
from ...relay import ConnectionField
from ...relay.utils import is_node
from .utils import get_type_for_model, lazy_map


class DjangoConnectionField(ConnectionField):

    def wrap_resolved(self, value, instance, args, info):
        return lazy_map(value, self.type)


class LazyListField(Field):

    def get_type(self, schema):
        return List(self.type)

    def resolver(self, instance, args, info):
        resolved = super(LazyListField, self).resolver(instance, args, info)
        return lazy_map(resolved, self.type)


class ConnectionOrListField(Field):

    def internal_type(self, schema):
        model_field = self.type
        field_object_type = model_field.get_object_type(schema)
        if not field_object_type:
            raise SkipField()
        if is_node(field_object_type):
            field = DjangoConnectionField(field_object_type)
        else:
            field = LazyListField(field_object_type)
        field.contribute_to_class(self.object_type, self.name)
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
