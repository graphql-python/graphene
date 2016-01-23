from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.orm.query import Query

from graphene.utils import LazyList


def get_type_for_model(schema, model):
    schema = schema
    types = schema.types.values()
    for _type in types:
        type_model = hasattr(_type, '_meta') and getattr(
            _type._meta, 'model', None)
        if model == type_model:
            return _type


def get_session(info):
    schema = info.schema.graphene_schema
    return schema.options.get('session')


def get_query(model, info):
    query = getattr(model, 'query', None)
    if not query:
        session = get_session(info)
        if not session:
            raise Exception('A query in the model Base or a session in the schema is required for querying.\n'
                            'Read more http://graphene-python.org/docs/sqlalchemy/tips/#querying')
        query = session.query(model)
    return query


class WrappedQuery(LazyList):

    def __len__(self):
        # Dont calculate the length using len(query), as this will
        # evaluate the whole queryset and return it's length.
        # Use .count() instead
        return self._origin.count()


def maybe_query(value):
    if isinstance(value, Query):
        return WrappedQuery(value)
    return value


def is_mapped(obj):
    return isinstance(obj, DeclarativeMeta)
