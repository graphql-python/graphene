from ..objecttype import ObjectType
from ..schema import Schema
from ..uuid import UUID
from ..structures import NonNull


class Query(ObjectType):
    uuid = UUID(input=UUID())
    required_uuid = UUID(input=NonNull(UUID), required=True)

    def resolve_uuid(self, info, input):
        return input

    def resolve_required_uuid(self, info, input):
        return input


schema = Schema(query=Query)


def test_uuidstring_query():
    uuid_value = "dfeb3bcf-70fd-11e7-a61a-6003088f8204"
    result = schema.execute("""{ uuid(input: "%s") }""" % uuid_value)
    assert not result.errors
    assert result.data == {"uuid": uuid_value}


def test_uuidstring_query_variable():
    uuid_value = "dfeb3bcf-70fd-11e7-a61a-6003088f8204"

    result = schema.execute(
        """query Test($uuid: UUID){ uuid(input: $uuid) }""",
        variables={"uuid": uuid_value},
    )
    assert not result.errors
    assert result.data == {"uuid": uuid_value}


def test_uuidstring_invalid_argument():
    from graphql import version_info as graphql_version_info

    uuid_value = {"not": "a string"}

    result = schema.execute(
        """query Test($uuid: UUID){ uuid(input: $uuid) }""",
        variables={"uuid": uuid_value},
    )
    assert result.errors
    assert len(result.errors) == 1
    expected = (
        "Variable '$uuid' has invalid value: UUID cannot represent value: {'not': 'a string'}"
        if graphql_version_info >= (3, 3)
        else "Variable '$uuid' got invalid value {'not': 'a string'}; UUID cannot represent value: {'not': 'a string'}"
    )
    assert result.errors[0].message == expected


def test_uuidstring_optional_uuid_input():
    """
    Test that we can provide a null value to an optional input
    """
    result = schema.execute("{ uuid(input: null) }")
    assert not result.errors
    assert result.data == {"uuid": None}


def test_uuidstring_invalid_query():
    """
    Test that if an invalid type is provided we get an error
    """
    from graphql import version_info as graphql_version_info

    is_v33 = graphql_version_info >= (3, 3)
    sep = "found:" if is_v33 else "found"

    result = schema.execute("{ uuid(input: 1) }")
    assert result.errors
    assert len(result.errors) == 1
    assert result.errors[0].message == f"Expected value of type 'UUID', {sep} 1."

    result = schema.execute('{ uuid(input: "a") }')
    assert result.errors
    assert len(result.errors) == 1
    expected_bad_uuid = (
        "Expected value of type 'UUID', but encountered error "
        "'badly formed hexadecimal UUID string'; found: \"a\"."
        if is_v33
        else "Expected value of type 'UUID', found \"a\"; badly formed hexadecimal UUID string"
    )
    assert result.errors[0].message == expected_bad_uuid

    result = schema.execute("{ requiredUuid(input: null) }")
    assert result.errors
    assert len(result.errors) == 1
    expected_null_msg = (
        "Expected value of non-null type 'UUID!' not to be None."
        if is_v33
        else "Expected value of type 'UUID!', found null."
    )
    assert result.errors[0].message == expected_null_msg
