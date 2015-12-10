from functools import wraps
from graphql.core.utils.get_field_def import get_field_def
from graphql.core.type.definition import GraphQLList, GraphQLNonNull


def get_fields(info):
    field_asts = info.field_asts[0].selection_set.selections
    only_args = []
    _type = info.return_type
    if isinstance(_type, (GraphQLList, GraphQLNonNull)):
        _type = _type.of_type

    for field in field_asts:
        field_def = get_field_def(info.schema, _type, field)
        f = field_def.resolver
        fetch_field = getattr(f, 'django_fetch_field', None)
        if not fetch_field:
            continue
        only_args.append(fetch_field.attname)
    return only_args


def fetch_only_required(f):
    @wraps(f)
    def wrapper(*args):
        info = args[-1]
        return f(*args).only(*get_fields(info))
    return wrapper
