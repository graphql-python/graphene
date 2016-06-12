from collections import OrderedDict
from ..types.field import Field


def copy_fields(fields, **extra):
    _fields = []
    for attname, field in fields.items():
        field = Field.copy_and_extend(field, attname=attname, **extra)
        _fields.append(field)

    return OrderedDict((f.name, f) for f in _fields)
