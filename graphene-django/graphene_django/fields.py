# from ...core.exceptions import SkipField
from graphene import Field, List
from graphene.relay import ConnectionField
from .utils import DJANGO_FILTER_INSTALLED, get_type_for_model, maybe_queryset


class DjangoConnectionField(ConnectionField):

    def __init__(self, *args, **kwargs):
        self.on = kwargs.pop('on', False)
        # kwargs['default'] = kwargs.pop('default', self.get_manager)
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


def get_list_or_connection_type_for_model(model):
    pass
    # field_object_type = model_field.get_object_type(schema)
    # if not field_object_type:
    #     raise SkipField()
    # if isinstance(:
    #     if field_object_type._meta.filter_fields:
    #         field = DjangoFilterConnectionField(field_object_type)
    #     else:
    #         field = DjangoConnectionField(field_object_type)
    # else:
    #     field = List(field_object_type)
    # field.contribute_to_class(self.object_type, self.attname)
    # return schema.T(field)


def get_graphene_type_from_model(model):
    pass
    # _type = self.get_object_type(schema)
    # if not _type and self.parent._meta.only_fields:
    #     raise Exception(
    #         "Model %r is not accessible by the schema. "
    #         "You can either register the type manually "
    #         "using @schema.register. "
    #         "Or disable the field in %s" % (
    #             self.model,
    #             self.parent,
    #         )
    #     )
    # if not _type:
    #     raise SkipField()
    # return schema.T(_type)
