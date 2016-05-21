from ..utils import ProxySnakeDict


class CamelCaseArgsMiddleware(object):

    def resolve(self, next, root, args, context, info):
        args = ProxySnakeDict(args)
        return next(root, args, context, info)
