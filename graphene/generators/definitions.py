from graphql import GraphQLObjectType, GraphQLInterfaceType, GraphQLScalarType, GraphQLEnumType


class GrapheneGraphQLType(object):
    '''
    A class for extending the base GraphQLType with the related
    graphene_type
    '''
    def __init__(self, *args, **kwargs):
        self.graphene_type = kwargs.pop('graphene_type')
        super(GrapheneGraphQLType, self).__init__(*args, **kwargs)


class GrapheneInterfaceType(GrapheneGraphQLType, GraphQLInterfaceType):
    pass


class GrapheneObjectType(GrapheneGraphQLType, GraphQLObjectType):

    def __init__(self, *args, **kwargs):
        super(GrapheneObjectType, self).__init__(*args, **kwargs)
        self.check_interfaces()

    def check_interfaces(self):
        if not self._provided_interfaces:
            return
        for interface in self._provided_interfaces:
            if isinstance(interface, GrapheneInterfaceType):
                interface.graphene_type.implements(self.graphene_type)


class GrapheneScalarType(GrapheneGraphQLType, GraphQLScalarType):
    pass


class GrapheneEnumType(GrapheneGraphQLType, GraphQLEnumType):
    pass
