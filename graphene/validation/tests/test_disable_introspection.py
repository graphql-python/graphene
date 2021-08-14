from graphql import parse, validate

from ...types import Schema, ObjectType, String
from ..disable_introspection import disable_introspection


class Query(ObjectType):
    name = String(
        required=True
    )


schema = Schema(query=Query)


def run_query(query: str):
    document = parse(query)

    result = None

    errors = validate(
        schema=schema.graphql_schema,
        document_ast=document,
        rules=(
            disable_introspection(),
        ),
    )

    return errors, result
