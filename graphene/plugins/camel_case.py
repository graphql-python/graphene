from ..core.types.base import GroupNamedType
from ..utils import memoize, to_camel_case
from .base import Plugin


def camelcase_named_type(schema, type):
    name = type.name or to_camel_case(type.attname)
    return name, schema.T(type)


class CamelCase(Plugin):

    @memoize
    def transform_group(self, _type):
        new_type = _type.__class__(*_type.types)
        setattr(new_type, 'get_named_type', camelcase_named_type)
        return new_type

    def transform_type(self, _type):
        if isinstance(_type, GroupNamedType):
            return self.transform_group(_type)
        return _type
