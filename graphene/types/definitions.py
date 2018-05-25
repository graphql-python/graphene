from graphql import GraphQLEnumType
from graphql import GraphQLInputObjectType
from graphql import GraphQLInterfaceType
from graphql import GraphQLObjectType
from graphql import GraphQLScalarType
from graphql import GraphQLUnionType


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


class GrapheneUnionType(GrapheneGraphQLType, GraphQLUnionType):
    pass


class GrapheneObjectType(GrapheneGraphQLType, GraphQLObjectType):
    pass


class GrapheneScalarType(GrapheneGraphQLType, GraphQLScalarType):
    pass


class GrapheneEnumType(GrapheneGraphQLType, GraphQLEnumType):
    pass


class GrapheneInputObjectType(GrapheneGraphQLType, GraphQLInputObjectType):
    pass
