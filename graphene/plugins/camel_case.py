from ..utils import to_camel_case, ProxySnakeDict


class CamelCase(object):

    def get_default_namedtype_name(self, value):
        return to_camel_case(value)

    def process_aci(self, aci):
        aci.args = ProxySnakeDict(aci.args)
