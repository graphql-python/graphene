Batching
=====

Apollo Client has a network interface that supports `GraphQL transport batching`_.

Transport batching is used to batch requests together that would otherwise be sent individually.
This not only saves client and server resources but also enables more efficient batching and caching for requests between the GraphQL server and databases or storage services.


Setting up batching in Graphene-Django
--------------------------------------

Graphene-Django has built-in support for transport batching, which can be enabled by simply passing ``batch=true`` to your ``GraphQLView``: 

.. code:: python

    from django.conf.urls import url, include
    from django.contrib import admin

    from graphene_django.views import GraphQLView

    urlpatterns = [
        url(r'^graphql', GraphQLView.as_view(graphiql=True, batch=True)),
    ]



.. _GraphQL transport batching: http://dev.apollodata.com/core/network.html#query-batching