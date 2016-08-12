import inspect
from collections import OrderedDict

from graphql.type.typemap import GraphQLTypeMap

from .objecttype import ObjectType
from .structures import List, NonNull
from .scalars import Scalar, String, Boolean, Int, Float, ID

from graphql import GraphQLString, GraphQLField, GraphQLList, GraphQLBoolean, GraphQLInt, GraphQLFloat, GraphQLID, GraphQLNonNull


def is_graphene_type(_type):
    if isinstance(_type, (List, NonNull)):
        return True
    if inspect.isclass(_type) and issubclass(_type, (ObjectType, Scalar)):
        return True


class TypeMap(GraphQLTypeMap):

    @classmethod
    def reducer(cls, map, type):
        if not type:
            return map
        if is_graphene_type(type):
            return cls.graphene_reducer(map, type)
        return super(TypeMap, cls).reducer(map, type)

    @classmethod
    def graphene_reducer(cls, map, type):
        if isinstance(type, List):
            return cls.reducer(map, type.of_type)
            return map
        if type._meta.name in map:
            _type = map[type._meta.name]
            if is_graphene_type(_type):
                assert _type.graphene_type == type
            return map
        if issubclass(type, ObjectType):
            return cls.construct_objecttype(map, type)
        if issubclass(type, Scalar):
            return cls.construct_scalar(map, type)
        return map

    @classmethod
    def construct_scalar(cls, map, type):
        from ..generators.definitions import GrapheneScalarType
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

    @classmethod
    def construct_objecttype(cls, map, type):
        from ..generators.definitions import GrapheneObjectType
        map[type._meta.name] = GrapheneObjectType(
            graphene_type=type,
            name=type._meta.name,
            description=type._meta.description,
            fields={},
            is_type_of=type.is_type_of,
            interfaces=type._meta.interfaces
        )
        map[type._meta.name].fields = cls.construct_fields_for_type(map, type)
        return map

    @classmethod
    def construct_fields_for_type(cls, map, type):
        fields = OrderedDict()
        for name, field in type._meta.fields.items():
            map = cls.reducer(map, field.type)
            field_type = cls.get_field_type(map, field.type)
            _field = GraphQLField(
                field_type,
                args=field.args,
                resolver=field.resolver,
                deprecation_reason=field.deprecation_reason,
                description=field.description
            )
            fields[name] = _field
        return fields

    @classmethod
    def get_field_type(self, map, type):
        if isinstance(type, List):
            return GraphQLList(self.get_field_type(map, type.of_type))
        if isinstance(type, NonNull):
            return GraphQLNonNull(self.get_field_type(map, type.of_type))
        return map.get(type._meta.name)
