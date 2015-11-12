from django.conf.urls import url

import graphene
from graphene import Schema
from graphene.contrib.django.types import DjangoNode
from graphene.contrib.django.views import GraphQLView

from .models import Article, Reporter


class Character(DjangoNode):

    class Meta:
        model = Reporter

    def get_node(self, id):
        pass


class Human(DjangoNode):
    raises = graphene.String()

    class Meta:
        model = Article

    def resolve_raises(self, *args):
        raise Exception("This field should raise exception")

    def get_node(self, id):
        pass

schema = Schema(query=Human)


urlpatterns = [
    url(r'^graphql', GraphQLView.as_view(schema=schema)),
]
