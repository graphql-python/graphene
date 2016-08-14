import graphene
from graphene import Schema
from ..types import DjangoNode, DjangoObjectType

from .models import Article, Reporter


class Character(DjangoObjectType):

    class Meta:
        model = Reporter
        interfaces = (DjangoNode, )

    def get_node(self, id, context, info):
        pass


class Human(DjangoObjectType):
    raises = graphene.String()

    class Meta:
        model = Article
        interfaces = (DjangoNode, )

    def resolve_raises(self, *args):
        raise Exception("This field should raise exception")

    def get_node(self, id):
        pass


class Query(graphene.ObjectType):
    human = graphene.Field(Human)

    def resolve_human(self, args, context, info):
        return Human()


schema = Schema(query=Query)
