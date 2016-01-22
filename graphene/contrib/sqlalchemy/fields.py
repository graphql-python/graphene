from ...core.exceptions import SkipField
from ...core.fields import Field
from ...core.types.base import FieldType
from ...core.types.definitions import List
from ...relay import ConnectionField
from ...relay.utils import is_node
from .utils import get_type_for_model


class SQLAlchemyConnectionField(ConnectionField):

    def __init__(self, *args, **kwargs):
        self.session = kwargs.pop('session', None)
        return super(SQLAlchemyConnectionField, self).__init__(*args, **kwargs)

    @property
    def model(self):
        return self.type._meta.model

    def get_session(self, args, info):
        return self.session

    def get_query(self, resolved_query, args, info):
        self.get_session(args, info)
        return resolved_query

    def from_list(self, connection_type, resolved, args, info):
        qs = self.get_query(resolved, args, info)
        return super(SQLAlchemyConnectionField, self).from_list(connection_type, qs, args, info)


class ConnectionOrListField(Field):

    def internal_type(self, schema):
        model_field = self.type
        field_object_type = model_field.get_object_type(schema)
        if not field_object_type:
            raise SkipField()
        if is_node(field_object_type):
            field = SQLAlchemyConnectionField(field_object_type)
        else:
            field = Field(List(field_object_type))
        field.contribute_to_class(self.object_type, self.attname)
        return schema.T(field)


class SQLAlchemyModelField(FieldType):

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super(SQLAlchemyModelField, self).__init__(*args, **kwargs)

    def internal_type(self, schema):
        _type = self.get_object_type(schema)
        if not _type and self.parent._meta.only_fields:
            raise Exception(
                "Table %r is not accessible by the schema. "
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
