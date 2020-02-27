import inspect
from functools import partial

from graphql import (
    default_type_resolver,
    get_introspection_query,
    graphql,
    graphql_sync,
    introspection_types,
    is_type,
    print_schema,
    GraphQLArgument,
    GraphQLBoolean,
    GraphQLEnumValue,
    GraphQLField,
    GraphQLFloat,
    GraphQLID,
    GraphQLInputField,
    GraphQLInt,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLString,
    Undefined,
)

from ..utils.str_converters import to_camel_case
from ..utils.get_unbound_function import get_unbound_function
from .definitions import (
    GrapheneEnumType,
    GrapheneGraphQLType,
    GrapheneInputObjectType,
    GrapheneInterfaceType,
    GrapheneObjectType,
    GrapheneScalarType,
    GrapheneUnionType,
)
from .dynamic import Dynamic
from .enum import Enum
from .field import Field
from .inputobjecttype import InputObjectType
from .interface import Interface
from .objecttype import ObjectType
from .resolver import get_default_resolver
from .scalars import ID, Boolean, Float, Int, Scalar, String
from .structures import List, NonNull
from .union import Union
from .utils import get_field_as

introspection_query = get_introspection_query()
IntrospectionSchema = introspection_types["__Schema"]


def assert_valid_root_type(type_):
    if type_ is None:
        return
    is_graphene_objecttype = inspect.isclass(type_) and issubclass(type_, ObjectType)
    is_graphql_objecttype = isinstance(type_, GraphQLObjectType)
    assert is_graphene_objecttype or is_graphql_objecttype, (
        "Type {} is not a valid ObjectType."
    ).format(type_)


def is_graphene_type(type_):
    if isinstance(type_, (List, NonNull)):
        return True
    if inspect.isclass(type_) and issubclass(
        type_, (ObjectType, InputObjectType, Scalar, Interface, Union, Enum)
    ):
        return True


def resolve_type(resolve_type_func, map_, type_name, root, info, _type):
    type_ = resolve_type_func(root, info)

    if not type_:
        return_type = map_[type_name]
        return default_type_resolver(root, info, return_type)

    if inspect.isclass(type_) and issubclass(type_, ObjectType):
        graphql_type = map_.get(type_._meta.name)
        assert graphql_type, "Can't find type {} in schema".format(type_._meta.name)
        assert graphql_type.graphene_type == type_, (
            "The type {} does not match with the associated graphene type {}."
        ).format(type_, graphql_type.graphene_type)
        return graphql_type

    return type_


def is_type_of_from_possible_types(possible_types, root, _info):
    return isinstance(root, possible_types)


class GrapheneGraphQLSchema(GraphQLSchema):
    """A GraphQLSchema that can deal with Graphene types as well."""

    def __init__(
        self,
        query=None,
        mutation=None,
        subscription=None,
        types=None,
        directives=None,
        auto_camelcase=True,
    ):
        assert_valid_root_type(query)
        assert_valid_root_type(mutation)
        assert_valid_root_type(subscription)

        self.auto_camelcase = auto_camelcase
        super().__init__(query, mutation, subscription, types, directives)

        if query:
            self.query_type = self.get_type(
                query.name if isinstance(query, GraphQLObjectType) else query._meta.name
            )
        if mutation:
            self.mutation_type = self.get_type(
                mutation.name
                if isinstance(mutation, GraphQLObjectType)
                else mutation._meta.name
            )
        if subscription:
            self.subscription_type = self.get_type(
                subscription.name
                if isinstance(subscription, GraphQLObjectType)
                else subscription._meta.name
            )

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

    # noinspection PyMethodOverriding
    def type_map_reducer(self, map_, type_):
        if not type_:
            return map_
        if inspect.isfunction(type_):
            type_ = type_()
        if is_graphene_type(type_):
            return self.graphene_reducer(map_, type_)
        return super().type_map_reducer(map_, type_)

    def graphene_reducer(self, map_, type_):
        if isinstance(type_, (List, NonNull)):
            return self.type_map_reducer(map_, type_.of_type)
        if type_._meta.name in map_:
            _type = map_[type_._meta.name]
            if isinstance(_type, GrapheneGraphQLType):
                assert _type.graphene_type == type_, (
                    "Found different types with the same name in the schema: {}, {}."
                ).format(_type.graphene_type, type_)
            return map_

        if issubclass(type_, ObjectType):
            internal_type = self.construct_objecttype(map_, type_)
        elif issubclass(type_, InputObjectType):
            internal_type = self.construct_inputobjecttype(map_, type_)
        elif issubclass(type_, Interface):
            internal_type = self.construct_interface(map_, type_)
        elif issubclass(type_, Scalar):
            internal_type = self.construct_scalar(type_)
        elif issubclass(type_, Enum):
            internal_type = self.construct_enum(type_)
        elif issubclass(type_, Union):
            internal_type = self.construct_union(map_, type_)
        else:
            raise Exception("Expected Graphene type, but received: {}.".format(type_))

        return super().type_map_reducer(map_, internal_type)

    @staticmethod
    def construct_scalar(type_):
        # We have a mapping to the original GraphQL types
        # so there are no collisions.
        _scalars = {
            String: GraphQLString,
            Int: GraphQLInt,
            Float: GraphQLFloat,
            Boolean: GraphQLBoolean,
            ID: GraphQLID,
        }
        if type_ in _scalars:
            return _scalars[type_]

        return GrapheneScalarType(
            graphene_type=type_,
            name=type_._meta.name,
            description=type_._meta.description,
            serialize=getattr(type_, "serialize", None),
            parse_value=getattr(type_, "parse_value", None),
            parse_literal=getattr(type_, "parse_literal", None),
        )

    @staticmethod
    def construct_enum(type_):
        values = {}
        for name, value in type_._meta.enum.__members__.items():
            description = getattr(value, "description", None)
            deprecation_reason = getattr(value, "deprecation_reason", None)
            if not description and callable(type_._meta.description):
                description = type_._meta.description(value)

            if not deprecation_reason and callable(type_._meta.deprecation_reason):
                deprecation_reason = type_._meta.deprecation_reason(value)

            values[name] = GraphQLEnumValue(
                value=value.value,
                description=description,
                deprecation_reason=deprecation_reason,
            )

        type_description = (
            type_._meta.description(None)
            if callable(type_._meta.description)
            else type_._meta.description
        )

        return GrapheneEnumType(
            graphene_type=type_,
            values=values,
            name=type_._meta.name,
            description=type_description,
        )

    def construct_objecttype(self, map_, type_):
        if type_._meta.name in map_:
            _type = map_[type_._meta.name]
            if isinstance(_type, GrapheneGraphQLType):
                assert _type.graphene_type == type_, (
                    "Found different types with the same name in the schema: {}, {}."
                ).format(_type.graphene_type, type_)
            return _type

        def interfaces():
            interfaces = []
            for interface in type_._meta.interfaces:
                self.graphene_reducer(map_, interface)
                internal_type = map_[interface._meta.name]
                assert internal_type.graphene_type == interface
                interfaces.append(internal_type)
            return interfaces

        if type_._meta.possible_types:
            is_type_of = partial(
                is_type_of_from_possible_types, type_._meta.possible_types
            )
        else:
            is_type_of = type_.is_type_of

        return GrapheneObjectType(
            graphene_type=type_,
            name=type_._meta.name,
            description=type_._meta.description,
            fields=partial(self.construct_fields_for_type, map_, type_),
            is_type_of=is_type_of,
            interfaces=interfaces,
        )

    def construct_interface(self, map_, type_):
        if type_._meta.name in map_:
            _type = map_[type_._meta.name]
            if isinstance(_type, GrapheneInterfaceType):
                assert _type.graphene_type == type_, (
                    "Found different types with the same name in the schema: {}, {}."
                ).format(_type.graphene_type, type_)
            return _type

        _resolve_type = None
        if type_.resolve_type:
            _resolve_type = partial(
                resolve_type, type_.resolve_type, map_, type_._meta.name
            )
        return GrapheneInterfaceType(
            graphene_type=type_,
            name=type_._meta.name,
            description=type_._meta.description,
            fields=partial(self.construct_fields_for_type, map_, type_),
            resolve_type=_resolve_type,
        )

    def construct_inputobjecttype(self, map_, type_):
        return GrapheneInputObjectType(
            graphene_type=type_,
            name=type_._meta.name,
            description=type_._meta.description,
            out_type=type_._meta.container,
            fields=partial(
                self.construct_fields_for_type, map_, type_, is_input_type=True
            ),
        )

    def construct_union(self, map_, type_):
        _resolve_type = None
        if type_.resolve_type:
            _resolve_type = partial(
                resolve_type, type_.resolve_type, map_, type_._meta.name
            )

        def types():
            union_types = []
            for objecttype in type_._meta.types:
                self.graphene_reducer(map_, objecttype)
                internal_type = map_[objecttype._meta.name]
                assert internal_type.graphene_type == objecttype
                union_types.append(internal_type)
            return union_types

        return GrapheneUnionType(
            graphene_type=type_,
            name=type_._meta.name,
            description=type_._meta.description,
            types=types,
            resolve_type=_resolve_type,
        )

    def get_name(self, name):
        if self.auto_camelcase:
            return to_camel_case(name)
        return name

    def construct_fields_for_type(self, map_, type_, is_input_type=False):
        fields = {}
        for name, field in type_._meta.fields.items():
            if isinstance(field, Dynamic):
                field = get_field_as(field.get_type(self), _as=Field)
                if not field:
                    continue
            map_ = self.type_map_reducer(map_, field.type)
            field_type = self.get_field_type(map_, field.type)
            if is_input_type:
                _field = GraphQLInputField(
                    field_type,
                    default_value=field.default_value,
                    out_name=name,
                    description=field.description,
                )
            else:
                args = {}
                for arg_name, arg in field.args.items():
                    map_ = self.type_map_reducer(map_, arg.type)
                    arg_type = self.get_field_type(map_, arg.type)
                    processed_arg_name = arg.name or self.get_name(arg_name)
                    args[processed_arg_name] = GraphQLArgument(
                        arg_type,
                        out_name=arg_name,
                        description=arg.description,
                        default_value=Undefined
                        if isinstance(arg.type, NonNull)
                        else arg.default_value,
                    )
                _field = GraphQLField(
                    field_type,
                    args=args,
                    resolve=field.get_resolver(
                        self.get_resolver_for_type(type_, name, field.default_value)
                    ),
                    deprecation_reason=field.deprecation_reason,
                    description=field.description,
                )
            field_name = field.name or self.get_name(name)
            fields[field_name] = _field
        return fields

    def get_resolver_for_type(self, type_, name, default_value):
        if not issubclass(type_, ObjectType):
            return
        resolver = getattr(type_, "resolve_{}".format(name), None)
        if not resolver:
            # If we don't find the resolver in the ObjectType class, then try to
            # find it in each of the interfaces
            interface_resolver = None
            for interface in type_._meta.interfaces:
                if name not in interface._meta.fields:
                    continue
                interface_resolver = getattr(interface, "resolve_{}".format(name), None)
                if interface_resolver:
                    break
            resolver = interface_resolver

        # Only if is not decorated with classmethod
        if resolver:
            return get_unbound_function(resolver)

        default_resolver = type_._meta.default_resolver or get_default_resolver()
        return partial(default_resolver, name, default_value)

    def get_field_type(self, map_, type_):
        if isinstance(type_, List):
            return GraphQLList(self.get_field_type(map_, type_.of_type))
        if isinstance(type_, NonNull):
            return GraphQLNonNull(self.get_field_type(map_, type_.of_type))
        return map_.get(type_._meta.name)


class Schema:
    """Schema Definition.

    A Graphene Schema can execute operations (query, mutation, subscription) against the defined
    types. For advanced purposes, the schema can be used to lookup type definitions and answer
    questions about the types through introspection.

    Args:
        query (ObjectType): Root query *ObjectType*. Describes entry point for fields to *read*
            data in your Schema.
        mutation (ObjectType, optional): Root mutation *ObjectType*. Describes entry point for
            fields to *create, update or delete* data in your API.
        subscription (ObjectType, optional): Root subscription *ObjectType*. Describes entry point
            for fields to receive continuous updates.
        directives (List[GraphQLDirective], optional): List of custom directives to include in the
            GraphQL schema. Defaults to only include directives defined by GraphQL spec (@include
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
        types=None,
        directives=None,
        auto_camelcase=True,
    ):
        self.query = query
        self.mutation = mutation
        self.subscription = subscription
        self.graphql_schema = GrapheneGraphQLSchema(
            query,
            mutation,
            subscription,
            types,
            directives,
            auto_camelcase=auto_camelcase,
        )

    def __str__(self):
        return print_schema(self.graphql_schema)

    def __getattr__(self, type_name):
        """
        This function let the developer select a type in a given schema
        by accessing its attrs.

        Example: using schema.Query for accessing the "Query" type in the Schema
        """
        _type = self.graphql_schema.get_type(type_name)
        if _type is None:
            raise AttributeError('Type "{}" not found in the Schema'.format(type_name))
        if isinstance(_type, GrapheneGraphQLType):
            return _type.graphene_type
        return _type

    def lazy(self, _type):
        return lambda: self.get_type(_type)

    def execute(self, *args, **kwargs):
        """Execute a GraphQL query on the schema.

        Use the `graphql_sync` function from `graphql-core` to provide the result
        for a query string. Most of the time this method will be called by one of the Graphene
        :ref:`Integrations` via a web request.

        Args:
            request_string (str or Document): GraphQL request (query, mutation or subscription)
                as string or parsed AST form from `graphql-core`.
            root_value (Any, optional): Value to use as the parent value object when resolving
                root types.
            context_value (Any, optional): Value to be made available to all resolvers via
                `info.context`. Can be used to share authorization, dataloaders or other
                information needed to resolve an operation.
            variable_values (dict, optional): If variables are used in the request string, they can
                be provided in dictionary form mapping the variable name to the variable value.
            operation_name (str, optional): If multiple operations are provided in the
                request_string, an operation name must be provided for the result to be provided.
            middleware (List[SupportsGraphQLMiddleware]): Supply request level middleware as
                defined in `graphql-core`.

        Returns:
            :obj:`ExecutionResult` containing any data and errors for the operation.
        """
        kwargs = normalize_execute_kwargs(kwargs)
        return graphql_sync(self.graphql_schema, *args, **kwargs)

    async def execute_async(self, *args, **kwargs):
        """Execute a GraphQL query on the schema asynchronously.

        Same as `execute`, but uses `graphql` instead of `graphql_sync`.
        """
        kwargs = normalize_execute_kwargs(kwargs)
        return await graphql(self.graphql_schema, *args, **kwargs)

    def introspect(self):
        introspection = self.execute(introspection_query)
        if introspection.errors:
            raise introspection.errors[0]
        return introspection.data


def normalize_execute_kwargs(kwargs):
    """Replace alias names in keyword arguments for graphql()"""
    if "root" in kwargs and "root_value" not in kwargs:
        kwargs["root_value"] = kwargs.pop("root")
    if "context" in kwargs and "context_value" not in kwargs:
        kwargs["context_value"] = kwargs.pop("context")
    if "variables" in kwargs and "variable_values" not in kwargs:
        kwargs["variable_values"] = kwargs.pop("variables")
    if "operation" in kwargs and "operation_name" not in kwargs:
        kwargs["operation_name"] = kwargs.pop("operation")
    return kwargs
