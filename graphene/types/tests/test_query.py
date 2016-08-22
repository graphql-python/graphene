from functools import partial

from graphql import execute, Source, parse

from ..objecttype import ObjectType
from ..scalars import String, Int
from ..schema import Schema
from ..structures import List


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


def test_big_list_query_benchmark(benchmark):
    big_list = range(10000)

    class Query(ObjectType):
        all_ints = List(Int)

        def resolve_all_ints(self, args, context, info):
            return big_list

    hello_schema = Schema(Query)

    big_list_query = partial(hello_schema.execute, '{ allInts }')
    result = benchmark(big_list_query)
    assert not result.errors
    assert result.data == {'allInts': list(big_list)}


def test_big_list_query_compiled_query_benchmark(benchmark):
    big_list = range(100000)

    class Query(ObjectType):
        all_ints = List(Int)

        def resolve_all_ints(self, args, context, info):
            return big_list

    hello_schema = Schema(Query)
    source = Source('{ allInts }')
    query_ast = parse(source)

    big_list_query = partial(execute, hello_schema, query_ast)
    result = benchmark(big_list_query)
    assert not result.errors
    assert result.data == {'allInts': list(big_list)}


def test_big_list_of_containers_query_benchmark(benchmark):
    class Container(ObjectType):
        x = Int()

    big_container_list = [Container(x=x) for x in range(1000)]

    class Query(ObjectType):
        all_containers = List(Container)

        def resolve_all_containers(self, args, context, info):
            return big_container_list

    hello_schema = Schema(Query)

    big_list_query = partial(hello_schema.execute, '{ allContainers { x } }')
    result = benchmark(big_list_query)
    assert not result.errors
    assert result.data == {'allContainers': [{'x': c.x} for c in big_container_list]}


def test_big_list_of_containers_multiple_fields_query_benchmark(benchmark):
    class Container(ObjectType):
        x = Int()
        y = Int()
        z = Int()
        o = Int()

    big_container_list = [Container(x=x, y=x, z=x, o=x) for x in range(1000)]

    class Query(ObjectType):
        all_containers = List(Container)

        def resolve_all_containers(self, args, context, info):
            return big_container_list

    hello_schema = Schema(Query)

    big_list_query = partial(hello_schema.execute, '{ allContainers { x, y, z, o } }')
    result = benchmark(big_list_query)
    assert not result.errors
    assert result.data == {'allContainers': [{'x': c.x, 'y': c.y, 'z': c.z, 'o': c.o} for c in big_container_list]}


def test_big_list_of_containers_multiple_fields_custom_resolvers_query_benchmark(benchmark):
    class Container(ObjectType):
        x = Int()
        y = Int()
        z = Int()
        o = Int()

        def resolve_x(self, args, context, info):
            return self.x

        def resolve_y(self, args, context, info):
            return self.y

        def resolve_z(self, args, context, info):
            return self.z

        def resolve_o(self, args, context, info):
            return self.o

    big_container_list = [Container(x=x, y=x, z=x, o=x) for x in range(1000)]

    class Query(ObjectType):
        all_containers = List(Container)

        def resolve_all_containers(self, args, context, info):
            return big_container_list

    hello_schema = Schema(Query)

    big_list_query = partial(hello_schema.execute, '{ allContainers { x, y, z, o } }')
    result = benchmark(big_list_query)
    assert not result.errors
    assert result.data == {'allContainers': [{'x': c.x, 'y': c.y, 'z': c.z, 'o': c.o} for c in big_container_list]}
