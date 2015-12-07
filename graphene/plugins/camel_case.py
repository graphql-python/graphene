from ..utils import to_camel_case
from .base import Plugin


class CamelCase(Plugin):

    def get_default_namedtype_name(self, value):
        return to_camel_case(value)
