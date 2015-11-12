from graphene import relay
from graphene.contrib.django.utils import get_type_for_model, lazy_map
from graphene.core.exceptions import SkipField
from graphene.core.fields import Field
from graphene.core.types.base import FieldType
from graphene.core.types.definitions import List
from graphene.relay.utils import is_node


class DjangoConnectionField(relay.ConnectionField):

    def wrap_resolved(self, value, instance, args, info):
        schema = info.schema.graphene_schema
        return lazy_map(value, self.type.get_object_type(schema))


class LazyListField(Field):

    def get_type(self, schema):
        return List(self.type)

    def resolver(self, instance, args, info):
        schema = info.schema.graphene_schema
        resolved = super(LazyListField, self).resolver(instance, args, info)
        return lazy_map(resolved, self.get_object_type(schema))


class ConnectionOrListField(Field):

    def internal_type(self, schema):
        model_field = self.type
        field_object_type = model_field.get_object_type(schema)
        if is_node(field_object_type):
            field = DjangoConnectionField(model_field)
        else:
            field = LazyListField(model_field)
        field.contribute_to_class(self.object_type, self.name)
        return field.internal_type(schema)


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
