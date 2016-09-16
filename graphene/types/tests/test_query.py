import json
from functools import partial

from graphql import execute, Source, parse, GraphQLError

from ..objecttype import ObjectType
from ..field import Field
from ..inputfield import InputField
from ..inputobjecttype import InputObjectType
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


def test_query_default_value():
    class MyType(ObjectType):
        field = String()

    class Query(ObjectType):
        hello = Field(MyType, default_value=MyType(field='something else!'))

    hello_schema = Schema(Query)

    executed = hello_schema.execute('{ hello { field } }')
    assert not executed.errors
    assert executed.data == {'hello': {'field': 'something else!'}}


def test_query_wrong_default_value():
    class MyType(ObjectType):
        field = String()

    class Query(ObjectType):
        hello = Field(MyType, default_value='hello')

    hello_schema = Schema(Query)

    executed = hello_schema.execute('{ hello { field } }')
    assert len(executed.errors) == 1
    assert executed.errors[0].message == GraphQLError('Expected value of type "MyType" but got: str.').message
    assert executed.data is None


def test_query_resolve_function():
    class Query(ObjectType):
        hello = String()

        def resolve_hello(self, args, context, info):
            return 'World'

    hello_schema = Schema(Query)

    executed = hello_schema.execute('{ hello }')
    assert not executed.errors
    assert executed.data == {'hello': 'World'}


def test_query_arguments():
    class Query(ObjectType):
        test = String(a_str=String(), a_int=Int())

        def resolve_test(self, args, context, info):
            return json.dumps([self, args], separators=(',', ':'))

    test_schema = Schema(Query)

    result = test_schema.execute('{ test }', None)
    assert not result.errors
    assert result.data == {'test': '[null,{}]'}

    result = test_schema.execute('{ test(aStr: "String!") }', 'Source!')
    assert not result.errors
    assert result.data == {'test': '["Source!",{"a_str":"String!"}]'}

    result = test_schema.execute('{ test(aInt: -123, aStr: "String!") }', 'Source!')
    assert not result.errors
    assert result.data in [
        {'test': '["Source!",{"a_str":"String!","a_int":-123}]'},
        {'test': '["Source!",{"a_int":-123,"a_str":"String!"}]'}
    ]


def test_query_input_field():
    class Input(InputObjectType):
        a_field = String()
        recursive_field = InputField(lambda: Input)

    class Query(ObjectType):
        test = String(a_input=Input())

        def resolve_test(self, args, context, info):
            return json.dumps([self, args], separators=(',', ':'))

    test_schema = Schema(Query)

    result = test_schema.execute('{ test }', None)
    assert not result.errors
    assert result.data == {'test': '[null,{}]'}

    result = test_schema.execute('{ test(aInput: {aField: "String!"} ) }', 'Source!')
    assert not result.errors
    assert result.data == {'test': '["Source!",{"a_input":{"a_field":"String!"}}]'}

    result = test_schema.execute('{ test(aInput: {recursiveField: {aField: "String!"}}) }', 'Source!')
    assert not result.errors
    assert result.data == {'test': '["Source!",{"a_input":{"recursive_field":{"a_field":"String!"}}}]'}


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
