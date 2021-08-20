import inspect
from functools import partial

from graphql import (
    default_type_resolver,
    get_introspection_query,
    graphql,
    graphql_sync,
    introspection_types,
    parse,
    print_schema,
    subscribe,
    validate,
    ExecutionResult,
    GraphQLArgument,
    GraphQLBoolean,
    GraphQLError,
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
)
from graphql.execution import ExecutionContext
from graphql.execution.values import get_argument_values

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
    assert (
        is_graphene_objecttype or is_graphql_objecttype
    ), f"Type {type_} is not a valid ObjectType."


def is_graphene_type(type_):
    if isinstance(type_, (List, NonNull)):
        return True
    if inspect.isclass(type_) and issubclass(
        type_, (ObjectType, InputObjectType, Scalar, Interface, Union, Enum)
    ):
        return True


def is_type_of_from_possible_types(possible_types, root, _info):
    return isinstance(root, possible_types)


# We use this resolver for subscriptions
def identity_resolve(root, info, **arguments):
    return root


class TypeMap(dict):
    def __init__(
        self,
        query=None,
        mutation=None,
        subscription=None,
        types=None,
        auto_camelcase=True,
    ):
        assert_valid_root_type(query)
        assert_valid_root_type(mutation)
        assert_valid_root_type(subscription)
        if types is None:
            types = []
        for type_ in types:
            assert is_graphene_type(type_)

        self.auto_camelcase = auto_camelcase

        create_graphql_type = self.add_type

        self.query = create_graphql_type(query) if query else None
        self.mutation = create_graphql_type(mutation) if mutation else None
        self.subscription = create_graphql_type(subscription) if subscription else None

        self.types = [create_graphql_type(graphene_type) for graphene_type in types]

    def add_type(self, graphene_type):
        if inspect.isfunction(graphene_type):
            graphene_type = graphene_type()
        if isinstance(graphene_type, List):
            return GraphQLList(self.add_type(graphene_type.of_type))
        if isinstance(graphene_type, NonNull):
            return GraphQLNonNull(self.add_type(graphene_type.of_type))
        try:
            name = graphene_type._meta.name
        except AttributeError:
            raise TypeError(f"Expected Graphene type, but received: {graphene_type}.")
        graphql_type = self.get(name)
        if graphql_type:
            return graphql_type
        if issubclass(graphene_type, ObjectType):
            graphql_type = self.create_objecttype(graphene_type)
        elif issubclass(graphene_type, InputObjectType):
            graphql_type = self.create_inputobjecttype(graphene_type)
        elif issubclass(graphene_type, Interface):
            graphql_type = self.create_interface(graphene_type)
        elif issubclass(graphene_type, Scalar):
            graphql_type = self.create_scalar(graphene_type)
        elif issubclass(graphene_type, Enum):
            graphql_type = self.create_enum(graphene_type)
        elif issubclass(graphene_type, Union):
            graphql_type = self.construct_union(graphene_type)
        else:
            raise TypeError(f"Expected Graphene type, but received: {graphene_type}.")
        self[name] = graphql_type
        return graphql_type

    @staticmethod
    def create_scalar(graphene_type):
        # We have a mapping to the original GraphQL types
        # so there are no collisions.
        _scalars = {
            String: GraphQLString,
            Int: GraphQLInt,
            Float: GraphQLFloat,
            Boolean: GraphQLBoolean,
            ID: GraphQLID,
        }
        if graphene_type in _scalars:
            return _scalars[graphene_type]

        return GrapheneScalarType(
            graphene_type=graphene_type,
            name=graphene_type._meta.name,
            description=graphene_type._meta.description,
            serialize=getattr(graphene_type, "serialize", None),
            parse_value=getattr(graphene_type, "parse_value", None),
            parse_literal=getattr(graphene_type, "parse_literal", None),
        )

    @staticmethod
    def create_enum(graphene_type):
        values = {}
        for name, value in graphene_type._meta.enum.__members__.items():
            description = getattr(value, "description", None)
            deprecation_reason = getattr(value, "deprecation_reason", None)
            if not description and callable(graphene_type._meta.description):
                description = graphene_type._meta.description(value)

            if not deprecation_reason and callable(
                graphene_type._meta.deprecation_reason
            ):
                deprecation_reason = graphene_type._meta.deprecation_reason(value)

            values[name] = GraphQLEnumValue(
                value=value,
                description=description,
                deprecation_reason=deprecation_reason,
            )

        type_description = (
            graphene_type._meta.description(None)
            if callable(graphene_type._meta.description)
            else graphene_type._meta.description
        )

        return GrapheneEnumType(
            graphene_type=graphene_type,
            values=values,
            name=graphene_type._meta.name,
            description=type_description,
        )

    def create_objecttype(self, graphene_type):
        create_graphql_type = self.add_type

        def interfaces():
            interfaces = []
            for graphene_interface in graphene_type._meta.interfaces:
                interface = create_graphql_type(graphene_interface)
                assert interface.graphene_type == graphene_interface
                interfaces.append(interface)
            return interfaces

        if graphene_type._meta.possible_types:
            is_type_of = partial(
                is_type_of_from_possible_types, graphene_type._meta.possible_types
            )
        else:
            is_type_of = graphene_type.is_type_of

        return GrapheneObjectType(
            graphene_type=graphene_type,
            name=graphene_type._meta.name,
            description=graphene_type._meta.description,
            fields=partial(self.create_fields_for_type, graphene_type),
            is_type_of=is_type_of,
            interfaces=interfaces,
        )

    def create_interface(self, graphene_type):
        resolve_type = (
            partial(
                self.resolve_type, graphene_type.resolve_type, graphene_type._meta.name
            )
            if graphene_type.resolve_type
            else None
        )

        return GrapheneInterfaceType(
            graphene_type=graphene_type,
            name=graphene_type._meta.name,
            description=graphene_type._meta.description,
            fields=partial(self.create_fields_for_type, graphene_type),
            resolve_type=resolve_type,
        )

    def create_inputobjecttype(self, graphene_type):
        return GrapheneInputObjectType(
            graphene_type=graphene_type,
            name=graphene_type._meta.name,
            description=graphene_type._meta.description,
            out_type=graphene_type._meta.container,
            fields=partial(
                self.create_fields_for_type, graphene_type, is_input_type=True
            ),
        )

    def construct_union(self, graphene_type):
        create_graphql_type = self.add_type

        def types():
            union_types = []
            for graphene_objecttype in graphene_type._meta.types:
                object_type = create_graphql_type(graphene_objecttype)
                assert object_type.graphene_type == graphene_objecttype
                union_types.append(object_type)
            return union_types

        resolve_type = (
            partial(
                self.resolve_type, graphene_type.resolve_type, graphene_type._meta.name
            )
            if graphene_type.resolve_type
            else None
        )

        return GrapheneUnionType(
            graphene_type=graphene_type,
            name=graphene_type._meta.name,
            description=graphene_type._meta.description,
            types=types,
            resolve_type=resolve_type,
        )

    def get_name(self, name):
        if self.auto_camelcase:
            return to_camel_case(name)
        return name

    def create_fields_for_type(self, graphene_type, is_input_type=False):
        create_graphql_type = self.add_type

        fields = {}
        for name, field in graphene_type._meta.fields.items():
            if isinstance(field, Dynamic):
                field = get_field_as(field.get_type(self), _as=Field)
                if not field:
                    continue
            field_type = create_graphql_type(field.type)
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
                    arg_type = create_graphql_type(arg.type)
                    processed_arg_name = arg.name or self.get_name(arg_name)
                    args[processed_arg_name] = GraphQLArgument(
                        arg_type,
                        out_name=arg_name,
                        description=arg.description,
                        default_value=arg.default_value,
                    )
                subscribe = field.wrap_subscribe(
                    self.get_function_for_type(
                        graphene_type, f"subscribe_{name}", name, field.default_value
                    )
                )

                # If we are in a subscription, we use (by default) an
                # identity-based resolver for the root, rather than the
                # default resolver for objects/dicts.
                if subscribe:
                    field_default_resolver = identity_resolve
                elif issubclass(graphene_type, ObjectType):
                    default_resolver = (
                        graphene_type._meta.default_resolver or get_default_resolver()
                    )
                    field_default_resolver = partial(
                        default_resolver, name, field.default_value
                    )
                else:
                    field_default_resolver = None

                resolve = field.wrap_resolve(
                    self.get_function_for_type(
                        graphene_type, f"resolve_{name}", name, field.default_value
                    )
                    or field_default_resolver
                )

                _field = GraphQLField(
                    field_type,
                    args=args,
                    resolve=resolve,
                    subscribe=subscribe,
                    deprecation_reason=field.deprecation_reason,
                    description=field.description,
                )
            field_name = field.name or self.get_name(name)
            fields[field_name] = _field
        return fields

    def get_function_for_type(self, graphene_type, func_name, name, default_value):
        """Gets a resolve or subscribe function for a given ObjectType"""
        if not issubclass(graphene_type, ObjectType):
            return
        resolver = getattr(graphene_type, func_name, None)
        if not resolver:
            # If we don't find the resolver in the ObjectType class, then try to
            # find it in each of the interfaces
            interface_resolver = None
            for interface in graphene_type._meta.interfaces:
                if name not in interface._meta.fields:
                    continue
                interface_resolver = getattr(interface, func_name, None)
                if interface_resolver:
                    break
            resolver = interface_resolver

        # Only if is not decorated with classmethod
        if resolver:
            return get_unbound_function(resolver)

    def resolve_type(self, resolve_type_func, type_name, root, info, _type):
        type_ = resolve_type_func(root, info)

        if not type_:
            return_type = self[type_name]
            return default_type_resolver(root, info, return_type)

        if inspect.isclass(type_) and issubclass(type_, ObjectType):
            graphql_type = self.get(type_._meta.name)
            assert graphql_type, f"Can't find type {type_._meta.name} in schema"
            assert (
                graphql_type.graphene_type == type_
            ), f"The type {type_} does not match with the associated graphene type {graphql_type.graphene_type}."
            return graphql_type

        return type_
