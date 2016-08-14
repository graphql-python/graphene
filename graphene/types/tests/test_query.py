

from ..objecttype import ObjectType
from ..scalars import String
from ..schema import Schema


def test_query():
    class Query(ObjectType):
        hello = String(resolver=lambda *_: 'World')

    hello_schema = Schema(Query)

    executed = hello_schema.execute('{ hello }')
    assert not executed.errors
    assert executed.data == {'hello': 'World'}


def test_query_resolve_function():
    class Query(ObjectType):
        hello = String()

        def resolve_hello(self, args, context, info):
            return 'World'

    hello_schema = Schema(Query)

    executed = hello_schema.execute('{ hello }')
    assert not executed.errors
    assert executed.data == {'hello': 'World'}


def test_query_middlewares():
    class Query(ObjectType):
        hello = String()
        other = String()

        def resolve_hello(self, args, context, info):
            return 'World'

        def resolve_other(self, args, context, info):
            return 'other'

    def reversed_middleware(next, *args, **kwargs):
        p = next(*args, **kwargs)
        return p.then(lambda x: x[::-1])

    hello_schema = Schema(Query, middlewares=[reversed_middleware])

    executed = hello_schema.execute('{ hello, other }')
    assert not executed.errors
    assert executed.data == {'hello': 'dlroW', 'other': 'rehto'}
