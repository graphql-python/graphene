from functools import wraps
from graphql.core.utils.get_field_def import get_field_def
from graphql.core.type.definition import GraphQLList, GraphQLNonNull


def get_resolvers(info):
    field_asts = info.field_asts[0].selection_set.selections
    _type = info.return_type
    if isinstance(_type, (GraphQLList, GraphQLNonNull)):
        _type = _type.of_type

    for field in field_asts:
        field_def = get_field_def(info.schema, _type, field)
        yield field_def.resolver


def get_fields(info):
    for resolver in get_resolvers(info):
        fetch_field = getattr(resolver, 'django_fetch_field', None)
        if not fetch_field:
            continue
        yield fetch_field.attname


def fetch_only_required(f):
    @wraps(f)
    def wrapper(*args):
        info = args[-1]
        return f(*args).only(*get_fields(info))
    return wrapper
