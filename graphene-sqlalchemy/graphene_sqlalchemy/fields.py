from sqlalchemy.orm.query import Query

from graphene.relay import ConnectionField
from graphql_relay.connection.arrayconnection import connection_from_list_slice
from .utils import get_query


class SQLAlchemyConnectionField(ConnectionField):

    @property
    def model(self):
        return self.connection._meta.node._meta.model

    def get_query(self, context):
        return get_query(self.model, context)

    def default_resolver(self, root, args, context, info):
        return getattr(root, self.source or self.attname, self.get_query(context))

    @staticmethod
    def connection_resolver(resolver, connection, root, args, context, info):
        iterable = resolver(root, args, context, info)
        if isinstance(iterable, Query):
            _len = iterable.count()
        else:
            _len = len(iterable)
        return connection_from_list_slice(
            iterable,
            args,
            slice_start=0,
            list_length=_len,
            list_slice_length=_len,
            connection_type=connection,
            edge_type=connection.Edge,
        )
