import graphene

import cookbook.ingredients.schema


class Query(cookbook.ingredients.schema.Query):
    pass

schema = graphene.Schema(name='Cookbook Schema')
schema.query = Query
