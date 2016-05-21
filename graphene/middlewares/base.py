from ..utils import promise_middleware

MIDDLEWARE_RESOLVER_FUNCTION = 'resolve'


class MiddlewareManager(object):

    def __init__(self, schema, middlewares=None):
        self.schema = schema
        self.middlewares = middlewares or []

    def add_middleware(self, middleware):
        self.middlewares.append(middleware)

    def get_middleware_resolvers(self):
        for middleware in self.middlewares:
            if not hasattr(middleware, MIDDLEWARE_RESOLVER_FUNCTION):
                continue
            yield getattr(middleware, MIDDLEWARE_RESOLVER_FUNCTION)

    def wrap(self, resolver):
        middleware_resolvers = self.get_middleware_resolvers()
        return promise_middleware(resolver, middleware_resolvers)
