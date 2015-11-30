import {
  GraphQLObjectType,
  GraphQLString,
  GraphQLSchema,
} from 'graphql';


export default new GraphQLSchema({
  query: new GraphQLObjectType({
    name: 'Query',
    fields: () => ({
      __emptyField: {type: GraphQLString},
    }),
  }),
});
