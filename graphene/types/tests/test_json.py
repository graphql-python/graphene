from ..json import JSONString
from ..objecttype import ObjectType
from ..schema import Schema


class Query(ObjectType):
    json = JSONString(input=JSONString())

    def resolve_json(self, info, input):
        return input


schema = Schema(query=Query)


def test_jsonstring_query():
    json_value = '{"key": "value"}'

    json_value_quoted = json_value.replace('"', '\\"')
    result = schema.execute("""{ json(input: "%s") }""" % json_value_quoted)
    assert not result.errors
    assert result.data == {"json": json_value}

    result = schema.execute("""{ json(input: "{}") }""")
    assert not result.errors
    assert result.data == {"json": "{}"}


def test_jsonstring_query_variable():
    json_value = '{"key": "value"}'

    result = schema.execute(
        """query Test($json: JSONString){ json(input: $json) }""",
        variables={"json": json_value},
    )
    assert not result.errors
    assert result.data == {"json": json_value}


def test_jsonstring_optional_uuid_input():
    """
    Test that we can provide a null value to an optional input
    """
    result = schema.execute("{ json(input: null) }")
    assert not result.errors
    assert result.data == {"json": None}


def test_jsonstring_invalid_query():
    """
    Test that if an invalid type is provided we get an error
    """
    from graphql import version_info as graphql_version_info

    is_v33 = graphql_version_info >= (3, 3)
    sep = "found:" if is_v33 else "found"

    result = schema.execute("{ json(input: 1) }")
    assert result.errors == [
        {"message": f"Expected value of type 'JSONString', {sep} 1."},
    ]

    result = schema.execute("{ json(input: {}) }")
    expected_obj_msg = (
        "Expected value of type 'JSONString', found: {  }."
        if is_v33
        else "Expected value of type 'JSONString', found {}."
    )
    assert result.errors == [{"message": expected_obj_msg}]

    result = schema.execute('{ json(input: "a") }')
    expected_bad_json_msg = (
        "Expected value of type 'JSONString', but encountered error "
        "'Badly formed JSONString: Expecting value: line 1 column 1 (char 0)'; "
        'found: "a".'
        if is_v33
        else "Expected value of type 'JSONString', found \"a\"; "
        "Badly formed JSONString: Expecting value: line 1 column 1 (char 0)"
    )
    assert result.errors == [{"message": expected_bad_json_msg}]

    result = schema.execute("""{ json(input: "{\\'key\\': 0}") }""")
    assert result.errors == [
        {"message": "Syntax Error: Invalid character escape sequence: '\\''."},
    ]

    result = schema.execute("""{ json(input: "{\\"key\\": 0,}") }""")
    assert len(result.errors) == 1
    expected_prefix = (
        "Expected value of type 'JSONString', but encountered error 'Badly formed JSONString:"
        if is_v33
        else 'Expected value of type \'JSONString\', found "{\\"key\\": 0,}"; Badly formed JSONString:'
    )
    assert result.errors[0].message.startswith(expected_prefix)
