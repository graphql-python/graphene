from django.http import HttpResponseNotAllowed
from django.http.response import HttpResponseBadRequest
from graphql.core import Source, parse, validate
from graphql.core.execution import ExecutionResult
from graphql.core.utils.get_operation_ast import get_operation_ast

from graphql_django_view import GraphQLView as BaseGraphQLView, HttpError


class GraphQLView(BaseGraphQLView):
    graphene_schema = None

    def __init__(self, schema, **kwargs):
        super(GraphQLView, self).__init__(
            graphene_schema=schema,
            schema=schema.schema,
            executor=schema.executor,
            **kwargs
        )

    def execute_graphql_request(self, request):
        query, variables, operation_name = self.get_graphql_params(request, self.parse_body(request))

        if not query:
            raise HttpError(HttpResponseBadRequest('Must provide query string.'))

        source = Source(query, name='GraphQL request')

        try:
            document_ast = parse(source)
        except Exception as e:
            return ExecutionResult(errors=[e], invalid=True)

        validation_errors = validate(self.schema, document_ast)
        if validation_errors:
            return ExecutionResult(invalid=True, errors=validation_errors)

        if request.method.lower() == 'get':
            operation_ast = get_operation_ast(document_ast, operation_name)
            if operation_ast and operation_ast.operation != 'query':
                raise HttpError(HttpResponseNotAllowed(
                    ['POST'], 'Can only perform a {} operation from a POST request.'.format(operation_ast.operation)
                ))

        try:
            return self.graphene_schema.execute(
                document_ast,
                self.get_root_value(request),
                variables,
                operation_name=operation_name,
                validate_ast=False,
                request_context=request
            )
        except Exception as e:
            return ExecutionResult(errors=[e], invalid=True)
