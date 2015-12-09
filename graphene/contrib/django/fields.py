import warnings

from ...core.exceptions import SkipField
from ...core.fields import Field
from ...core.types.base import FieldType
from ...core.types.definitions import List
from ...relay import ConnectionField
from ...relay.utils import is_node
from .utils import get_type_for_model


class DjangoField(Field):
    def decorate_resolver(self, resolver):
        f = super(DjangoField, self).decorate_resolver(resolver)
        setattr(f, 'django_fetch_field', self.field.name)
        return f

    def __init__(self, *args, **kwargs):
        self.field = kwargs.pop('_field')
        return super(DjangoField, self).__init__(*args, **kwargs)


class DjangoConnectionField(DjangoField, ConnectionField):

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        warnings.warn("Using {} will be not longer supported."
                      " Use relay.ConnectionField instead".format(cls.__name__),
                      FutureWarning)
        return super(DjangoConnectionField, self).__init__(*args, **kwargs)


class ConnectionOrListField(DjangoField):

    def internal_type(self, schema):
        model_field = self.type
        field_object_type = model_field.get_object_type(schema)
        if not field_object_type:
            raise SkipField()
        if is_node(field_object_type):
            field = DjangoConnectionField(field_object_type, _field=self.field)
        else:
            field = DjangoField(List(field_object_type), _field=self.field)
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
