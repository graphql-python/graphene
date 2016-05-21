from ..utils import to_camel_case, ProxySnakeDict


class CamelCase(object):

    def get_default_namedtype_name(self, value):
        return to_camel_case(value)

    def resolve(self, next, root, args, context, info):
        args = ProxySnakeDict(args)
        return next(root, args, context, info)
