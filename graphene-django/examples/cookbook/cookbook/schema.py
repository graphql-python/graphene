import cookbook.ingredients.schema
import graphene


class Query(cookbook.ingredients.schema.Query):
    pass

schema = graphene.Schema(name='Cookbook Schema', query=Query)
