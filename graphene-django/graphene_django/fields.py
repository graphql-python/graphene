from django.db.models.query import QuerySet
from graphene.relay import ConnectionField
from graphql_relay.connection.arrayconnection import connection_from_list_slice
from .utils import maybe_queryset, DJANGO_FILTER_INSTALLED


class DjangoConnectionField(ConnectionField):

    def __init__(self, *args, **kwargs):
        self.on = kwargs.pop('on', False)
        return super(DjangoConnectionField, self).__init__(*args, **kwargs)

    @property
    def model(self):
        return self.connection._meta.node._meta.model

    def get_manager(self):
        if self.on:
            return getattr(self.model, self.on)
        else:
            return self.model._default_manager

    def default_resolver(self, root, args, context, info):
        return getattr(root, self.source or self.attname, self.get_manager())

    def connection_resolver(self, root, args, context, info):
        iterable = super(ConnectionField, self).resolver(root, args, context, info)
        iterable = maybe_queryset(iterable)
        if isinstance(iterable, QuerySet):
            _len = iterable.count()
        else:
            _len = len(iterable)
        return connection_from_list_slice(
            iterable,
            args,
            slice_start=0,
            list_length=_len,
            list_slice_length=_len,
            connection_type=self.connection,
            edge_type=self.connection.Edge,
        )


def get_connection_field(*args, **kwargs):
    if DJANGO_FILTER_INSTALLED:
        from .filter.fields import DjangoFilterConnectionField
        return DjangoFilterConnectionField(*args, **kwargs)
    return ConnectionField(*args, **kwargs)
