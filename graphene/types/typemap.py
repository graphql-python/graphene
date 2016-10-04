import inspect
from collections import OrderedDict
from functools import partial

from graphql import (GraphQLArgument, GraphQLBoolean, GraphQLField,
                     GraphQLFloat, GraphQLID, GraphQLInputObjectField,
                     GraphQLInt, GraphQLList, GraphQLNonNull, GraphQLString)
from graphql.type import GraphQLEnumValue
from graphql.execution.executor import get_default_resolve_type_fn
from graphql.type.typemap import GraphQLTypeMap

from ..utils.str_converters import to_camel_case
from ..utils.get_unbound_function import get_unbound_function
from .dynamic import Dynamic
from .enum import Enum
from .inputobjecttype import InputObjectType
from .interface import Interface
from .objecttype import ObjectType
from .scalars import ID, Boolean, Float, Int, Scalar, String
from .structures import List, NonNull
from .union import Union


def is_graphene_type(_type):
    if isinstance(_type, (List, NonNull)):
        return True
    if inspect.isclass(_type) and issubclass(_type, (ObjectType, InputObjectType, Scalar, Interface, Union, Enum)):
        return True


def resolve_type(resolve_type_func, map, root, context, info):
    _type = resolve_type_func(root, context, info)
    # assert inspect.isclass(_type) and issubclass(_type, ObjectType), (
    #     'Received incompatible type "{}".'.format(_type)
    # )
    if not _type:
        return get_default_resolve_type_fn(root, context, info, info.return_type)

    if inspect.isclass(_type) and issubclass(_type, ObjectType):
        graphql_type = map.get(_type._meta.name)
        assert graphql_type and graphql_type.graphene_type == _type
        return graphql_type
    return _type


class TypeMap(GraphQLTypeMap):

    def __init__(self, types, auto_camelcase=True):
        self.auto_camelcase = auto_camelcase
        super(TypeMap, self).__init__(types)

    def reducer(self, map, type):
        if not type:
            return map
        if inspect.isfunction(type):
            type = type()
        if is_graphene_type(type):
            return self.graphene_reducer(map, type)
        return GraphQLTypeMap.reducer(map, type)

    def graphene_reducer(self, map, type):
        if isinstance(type, (List, NonNull)):
            return self.reducer(map, type.of_type)
        if type._meta.name in map:
            _type = map[type._meta.name]
            if is_graphene_type(_type):
                assert _type.graphene_type == type
            return map
        if issubclass(type, ObjectType):
            return self.construct_objecttype(map, type)
        if issubclass(type, InputObjectType):
            return self.construct_inputobjecttype(map, type)
        if issubclass(type, Interface):
            return self.construct_interface(map, type)
        if issubclass(type, Scalar):
            return self.construct_scalar(map, type)
        if issubclass(type, Enum):
            return self.construct_enum(map, type)
        if issubclass(type, Union):
            return self.construct_union(map, type)
        return map

    def construct_scalar(self, map, type):
        from .definitions import GrapheneScalarType
        _scalars = {
            String: GraphQLString,
            Int: GraphQLInt,
            Float: GraphQLFloat,
            Boolean: GraphQLBoolean,
            ID: GraphQLID
        }
        if type in _scalars:
            map[type._meta.name] = _scalars[type]
        else:
            map[type._meta.name] = GrapheneScalarType(
                graphene_type=type,
                name=type._meta.name,
                description=type._meta.description,

                serialize=getattr(type, 'serialize', None),
                parse_value=getattr(type, 'parse_value', None),
                parse_literal=getattr(type, 'parse_literal', None),
            )
        return map

    def construct_enum(self, map, type):
        from .definitions import GrapheneEnumType
        values = OrderedDict()
        for name, value in type._meta.enum.__members__.items():
            values[name] = GraphQLEnumValue(
                name=name,
                value=value.value,
                description=getattr(value, 'description', None),
                deprecation_reason=getattr(value, 'deprecation_reason', None)
            )
        map[type._meta.name] = GrapheneEnumType(
            graphene_type=type,
            values=values,
            name=type._meta.name,
            description=type._meta.description,
        )
        return map

    def construct_objecttype(self, map, type):
        from .definitions import GrapheneObjectType
        if type._meta.name in map:
            _type = map[type._meta.name]
            if is_graphene_type(_type):
                assert _type.graphene_type == type
            return map
        map[type._meta.name] = GrapheneObjectType(
            graphene_type=type,
            name=type._meta.name,
            description=type._meta.description,
            fields=None,
            is_type_of=type.is_type_of,
            interfaces=None
        )
        interfaces = []
        for i in type._meta.interfaces:
            map = self.reducer(map, i)
            interfaces.append(map[i._meta.name])
        map[type._meta.name]._provided_interfaces = interfaces
        map[type._meta.name]._fields = self.construct_fields_for_type(map, type)
        # self.reducer(map, map[type._meta.name])
        return map

    def construct_interface(self, map, type):
        from .definitions import GrapheneInterfaceType
        _resolve_type = None
        if type.resolve_type:
            _resolve_type = partial(resolve_type, type.resolve_type, map)
        map[type._meta.name] = GrapheneInterfaceType(
            graphene_type=type,
            name=type._meta.name,
            description=type._meta.description,
            fields=None,
            resolve_type=_resolve_type,
        )
        map[type._meta.name]._fields = self.construct_fields_for_type(map, type)
        # self.reducer(map, map[type._meta.name])
        return map

    def construct_inputobjecttype(self, map, type):
        from .definitions import GrapheneInputObjectType
        map[type._meta.name] = GrapheneInputObjectType(
            graphene_type=type,
            name=type._meta.name,
            description=type._meta.description,
            fields=None,
        )
        map[type._meta.name]._fields = self.construct_fields_for_type(map, type, is_input_type=True)
        return map

    def construct_union(self, map, type):
        from .definitions import GrapheneUnionType
        _resolve_type = None
        if type.resolve_type:
            _resolve_type = partial(resolve_type, type.resolve_type, map)
        types = []
        for i in type._meta.types:
            map = self.construct_objecttype(map, i)
            types.append(map[i._meta.name])
        map[type._meta.name] = GrapheneUnionType(
            graphene_type=type,
            name=type._meta.name,
            types=types,
            resolve_type=_resolve_type,
        )
        map[type._meta.name].types = types
        return map

    def get_name(self, name):
        if self.auto_camelcase:
            return to_camel_case(name)
        return name

    def default_resolver(self, attname, default_value, root, *_):
        return getattr(root, attname, default_value)

    def construct_fields_for_type(self, map, type, is_input_type=False):
        fields = OrderedDict()
        for name, field in type._meta.fields.items():
            if isinstance(field, Dynamic):
                field = field.get_type()
                if not field:
                    continue
            map = self.reducer(map, field.type)
            field_type = self.get_field_type(map, field.type)
            if is_input_type:
                _field = GraphQLInputObjectField(
                    field_type,
                    default_value=field.default_value,
                    out_name=field.name or name,
                    description=field.description
                )
            else:
                args = OrderedDict()
                for arg_name, arg in field.args.items():
                    map = self.reducer(map, arg.type)
                    arg_type = self.get_field_type(map, arg.type)
                    processed_arg_name = arg.name or self.get_name(arg_name)
                    args[processed_arg_name] = GraphQLArgument(
                        arg_type,
                        out_name=arg.name or arg_name,
                        description=arg.description,
                        default_value=arg.default_value
                    )
                _field = GraphQLField(
                    field_type,
                    args=args,
                    resolver=field.get_resolver(self.get_resolver_for_type(type, name, field.default_value)),
                    deprecation_reason=field.deprecation_reason,
                    description=field.description
                )
            field_name = field.name or self.get_name(name)
            fields[field_name] = _field
        return fields

    def get_resolver_for_type(self, type, name, default_value):
        if not issubclass(type, ObjectType):
            return
        resolver = getattr(type, 'resolve_{}'.format(name), None)
        if not resolver:
            # If we don't find the resolver in the ObjectType class, then try to
            # find it in each of the interfaces
            interface_resolver = None
            for interface in type._meta.interfaces:
                if name not in interface._meta.fields:
                    continue
                interface_resolver = getattr(interface, 'resolve_{}'.format(name), None)
                if interface_resolver:
                    break
            resolver = interface_resolver

        # Only if is not decorated with classmethod
        if resolver:
            return get_unbound_function(resolver)

        return partial(self.default_resolver, name, default_value)

    def get_field_type(self, map, type):
        if isinstance(type, List):
            return GraphQLList(self.get_field_type(map, type.of_type))
        if isinstance(type, NonNull):
            return GraphQLNonNull(self.get_field_type(map, type.of_type))
        if inspect.isfunction(type):
            type = type()
        return map.get(type._meta.name)
