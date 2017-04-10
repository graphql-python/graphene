from graphene.types.schema import Schema

from graphql.error import format_error


def format_execution_result(execution_result):
    if execution_result:
        response = {}

        if execution_result.errors:
            response['errors'] = [format_error(e) for e in execution_result.errors]

        if not execution_result.invalid:
            response['data'] = execution_result.data

        return response


class Client(object):
    def __init__(self, schema, **execute_options):
        assert isinstance(schema, Schema)
        self.schema = schema
        self.execute_options = execute_options

    def execute(self, *args, **kwargs):
        return format_execution_result(
            self.schema.execute(*args, **dict(self.execute_options, **kwargs))
        )
