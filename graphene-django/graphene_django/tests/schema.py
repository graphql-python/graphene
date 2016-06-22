import graphene
from graphene import Schema
from ..types import DjangoNode, DjangoObjectType

from .models import Article, Reporter


class Character(DjangoNode, DjangoObjectType):

    class Meta:
        model = Reporter

    def get_node(self, id, context, info):
        pass


class Human(DjangoNode, DjangoObjectType):
    raises = graphene.String()

    class Meta:
        model = Article

    def resolve_raises(self, *args):
        raise Exception("This field should raise exception")

    def get_node(self, id):
        pass


class Query(graphene.ObjectType):
    human = graphene.Field(Human)

    def resolve_human(self, args, context, info):
        return Human()


schema = Schema(query=Query)
