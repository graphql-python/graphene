from collections import OrderedDict
from ..types.field import Field, InputField


def copy_fields(like, fields, **extra):
    _fields = []
    for attname, field in fields.items():
        field = like.copy_and_extend(field, attname=getattr(field, 'attname', None) or attname, **extra)
        _fields.append(field)

    return OrderedDict((f.name, f) for f in _fields)
