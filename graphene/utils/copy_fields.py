from collections import OrderedDict

from ..types.field import Field, InputField


def copy_fields(like, fields, **extra):
    _fields = []
    for attname, field in fields.items():
        if isinstance(field, (Field, InputField)):
            copy_and_extend = field.copy_and_extend
        else:
            copy_and_extend = like.copy_and_extend
        field = copy_and_extend(field, attname=getattr(field, 'attname', None) or attname, **extra)
        _fields.append(field)

    return OrderedDict((f.name, f) for f in _fields)
