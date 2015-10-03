from django.conf.urls import url

from graphene.contrib.django.views import GraphQLView

from graphene import Schema
from graphene.contrib.django.types import (
    DjangoNode,
    DjangoInterface
)

from .models import Reporter, Article


class Character(DjangoNode):
    class Meta:
        model = Reporter

    def get_node(self, id):
        pass


class Human(DjangoNode):
    class Meta:
        model = Article

    def get_node(self, id):
        pass

schema = Schema(query=Human)


urlpatterns = [
    url(r'^graphql', GraphQLView.as_view(schema=schema)),
]
