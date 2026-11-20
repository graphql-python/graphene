from graphql import version_info as graphql_version_info

from ...types import ObjectType, Schema, String, NonNull


class Query(ObjectType):
    hello = String(input=NonNull(String))

    def resolve_hello(self, info, input):
        if input == "nothing":
            return None
        return f"Hello {input}!"


schema = Schema(query=Query)


def test_required_input_provided():
    """
    Test that a required argument works when provided.
    """
    input_value = "Potato"
    result = schema.execute('{ hello(input: "%s") }' % input_value)
    assert not result.errors
    assert result.data == {"hello": "Hello Potato!"}


def test_required_input_missing():
    """
    Test that a required argument raised an error if not provided.
    """
    result = schema.execute("{ hello }")
    assert result.errors
    assert len(result.errors) == 1
    expected_message = (
        "Argument 'Query.hello(input:)' of type 'String!' is required, but it was not provided."
        if graphql_version_info >= (3, 3)
        else "Field 'hello' argument 'input' of type 'String!' is required, but it was not provided."
    )
    assert result.errors[0].message == expected_message
