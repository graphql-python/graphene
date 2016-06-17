from django.conf.urls import include, url
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from cookbook.schema import schema
from graphene.contrib.django.views import GraphQLView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(schema=schema))),
    url(r'^graphiql', include('django_graphiql.urls')),
]
