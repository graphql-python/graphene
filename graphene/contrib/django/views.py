from graphql_django_view import GraphQLView as BaseGraphQLView


class GraphQLView(BaseGraphQLView):
    graphene_schema = None

    def __init__(self, schema, **kwargs):
        super(GraphQLView, self).__init__(
            graphene_schema=schema,
            schema=schema.schema,
            executor=schema.executor,
            **kwargs
        )

    def get_root_value(self, request):
        return self.graphene_schema.query(super(GraphQLView, self).get_root_value(request))
