from graphql_django_view import GraphQLView as BaseGraphQLView


class GraphQLView(BaseGraphQLView):
    def __init__(self, schema, **kwargs):
        super(GraphQLView, self).__init__(
            schema=schema.schema,
            executor=schema.executor,
            **kwargs
        )
