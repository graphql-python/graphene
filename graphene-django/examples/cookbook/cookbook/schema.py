import graphene
import cookbook.ingredients.schema

# print cookbook.ingredients.schema.Query._meta.graphql_type.get_fields()['allIngredients'].args

class Query(cookbook.ingredients.schema.Query):
    pass

schema = graphene.Schema(query=Query)
