import inspect

from graphql import GraphQLObjectType, GraphQLSchema, graphql, is_type
from graphql.type.directives import (
    GraphQLDirective,
    GraphQLIncludeDirective,
    GraphQLSkipDirective,
)
from graphql.type.introspection import IntrospectionSchema
from graphql.utils.introspection_query import introspection_query
from graphql.utils.schema_printer import print_schema

from .definitions import GrapheneGraphQLType
from .objecttype import ObjectType
from .typemap import TypeMap, is_graphene_type


def assert_valid_root_type(_type):
    if _type is None:
        return
    is_graphene_objecttype = inspect.isclass(_type) and issubclass(_type, ObjectType)
    is_graphql_objecttype = isinstance(_type, GraphQLObjectType)
    assert is_graphene_objecttype or is_graphql_objecttype, (
        "Type {} is not a valid ObjectType."
    ).format(_type)


class Schema(GraphQLSchema):
    """
    Graphene Schema can execute operations (query, mutation, subscription) against the defined
    types.

    For advanced purposes, the schema can be used to lookup type definitions and answer questions
    about the types through introspection.

    Args:
        query (ObjectType): Root query *ObjectType*. Describes entry point for fields to *read*
            data in your Schema.
        mutation (ObjectType, optional): Root mutation *ObjectType*. Describes entry point for
            fields to *create, update or delete* data in your API.
        subscription (ObjectType, optional): Root subscription *ObjectType*. Describes entry point
            for fields to receive continuous updates.
        directives (List[GraphQLDirective], optional): List of custom directives to include in
            GraphQL schema. Defaults to only include directives definved by GraphQL spec (@include
            and @skip) [GraphQLIncludeDirective, GraphQLSkipDirective].
        types (List[GraphQLType], optional): List of any types to include in schema that
            may not be introspected through root types.
        auto_camelcase (bool): Fieldnames will be transformed in Schema's TypeMap from snake_case
            to camelCase (preferred by GraphQL standard). Default True.
    """

    def __init__(
        self,
        query=None,
        mutation=None,
        subscription=None,
        directives=None,
        types=None,
        auto_camelcase=True,
    ):
        assert_valid_root_type(query)
        assert_valid_root_type(mutation)
        assert_valid_root_type(subscription)
        self._query = query
        self._mutation = mutation
        self._subscription = subscription
        self.types = types
        self.auto_camelcase = auto_camelcase
        if directives is None:
            directives = [GraphQLIncludeDirective, GraphQLSkipDirective]

        assert all(
            isinstance(d, GraphQLDirective) for d in directives
        ), "Schema directives must be List[GraphQLDirective] if provided but got: {}.".format(
            directives
        )
        self._directives = directives
        self.build_typemap()

    def get_query_type(self):
        return self.get_graphql_type(self._query)

    def get_mutation_type(self):
        return self.get_graphql_type(self._mutation)

    def get_subscription_type(self):
        return self.get_graphql_type(self._subscription)

    def __getattr__(self, type_name):
        """
        This function let the developer select a type in a given schema
        by accessing its attrs.

        Example: using schema.Query for accessing the "Query" type in the Schema
        """
        _type = super(Schema, self).get_type(type_name)
        if _type is None:
            raise AttributeError('Type "{}" not found in the Schema'.format(type_name))
        if isinstance(_type, GrapheneGraphQLType):
            return _type.graphene_type
        return _type

    def get_graphql_type(self, _type):
        if not _type:
            return _type
        if is_type(_type):
            return _type
        if is_graphene_type(_type):
            graphql_type = self.get_type(_type._meta.name)
            assert graphql_type, "Type {} not found in this schema.".format(
                _type._meta.name
            )
            assert graphql_type.graphene_type == _type
            return graphql_type
        raise Exception("{} is not a valid GraphQL type.".format(_type))

    def execute(self, *args, **kwargs):
        """
        Use the `graphql` function from `graphql-core` to provide the result for a query string.
        Most of the time this method will be called by one of the Graphene :ref:`Integrations`
        via a web request.

        Args:
            request_string (str or Document): GraphQL request (query, mutation or subscription) in
                string or parsed AST form from `graphql-core`.
            root (Any, optional): Value to use as the parent value object when resolving root
                types.
            context (Any, optional): Value to be made avaiable to all resolvers via
                `info.context`. Can be used to share authorization, dataloaders or other
                information needed to resolve an operation.
            variables (dict, optional): If variables are used in the request string, they can be
                provided in dictionary form mapping the variable name to the variable value.
            operation_name (str, optional): If mutiple operations are provided in the
                request_string, an operation name must be provided for the result to be provided.
            middleware (List[SupportsGraphQLMiddleware]): Supply request level middleware as
                defined in `graphql-core`.
            backend (GraphQLCoreBackend, optional): Override the default GraphQLCoreBackend.
            **execute_options (Any): Depends on backend selected. Default backend has several
                options such as: validate, allow_subscriptions, return_promise, executor.

        Returns:
            :obj:`ExecutionResult` containing any data and errors for the operation.
        """
        return graphql(self, *args, **kwargs)

    def introspect(self):
        instrospection = self.execute(introspection_query)
        if instrospection.errors:
            raise instrospection.errors[0]
        return instrospection.data

    def __str__(self):
        return print_schema(self)

    def lazy(self, _type):
        return lambda: self.get_type(_type)

    def build_typemap(self):
        initial_types = [
            self._query,
            self._mutation,
            self._subscription,
            IntrospectionSchema,
        ]
        if self.types:
            initial_types += self.types
        self._type_map = TypeMap(
            initial_types, auto_camelcase=self.auto_camelcase, schema=self
        )
