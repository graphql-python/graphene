from ..utils import to_camel_case


class CamelCase(object):

    def get_default_namedtype_name(self, value):
        return to_camel_case(value)
