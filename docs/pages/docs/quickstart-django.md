---
title: Django Tutorial
description: A Quick guide to Graphene in Django
---

# Django Tutorial

Graphene has a number of additional features that are designed to make
working with Django simple.

If you need help getting started with django then head over to
Django's getting started page.

First let's create a few simple models...

## Defining our models

Before continuing, create the following:

* A Django project called `cookbook`
* An app within `cookbook` called `ingredients`

Let's get started with these models:

```python
# cookbook/ingredients/models.py
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category)
```

## Schema

GraphQL presents your objects to the world as a graph structure rather than a more
hierarchical structure to which you may be accustomed. In order to create this
representation, Graphene needs to know about each *type* of object which will appear in
the graph. Below we define these as the `UserType` and `GroupType` classes.

This graph also has a 'root' through which all access begins. This is the `Query` class below.
In this example, we provide the ability to list all users via `all_users`, and the
ability to obtain a specific user via `get_user`.

Create `cookbook/ingredients/schema.py` and type the following:

```python
# cookbook/ingredients/schema.py
import graphene
from graphene.contrib.django import DjangoObjectType

from django.contrib.auth.models import User, Group

# Graphene will automatically map the User model's fields onto the UserType.
# This is configured in the UserType's Meta class (as you can see below)
class UserType(DjangoObjectType):
    class Meta:
        model = User
        only_fields = ('username', 'email', 'groups')


class GroupType(DjangoObjectType):
    class Meta:
        model = Group
        only_fields = ('name', )


class Query(graphene.ObjectType):
    get_user = graphene.Field(UserType,
                              id=graphene.String().NonNull)
    get_group = graphene.Field(GroupType,
                               id=graphene.String().NonNull)

schema = graphene.Schema(query=Query)
```


## Adding GraphiQL

For having the GraphiQL static assets we need to append `django_graphiql` in `INSTALLED_APPS` in `tutorial/settings.py`:

```python
INSTALLED_APPS = [
    # The other installed apps
    'django_graphiql',
]
```

## Creating GraphQL and GraphiQL views

Unlike a RESTful API, there is only a single URL from which a GraphQL is accessed.
Requests to this URL are handled by Graphene's `GraphQLView` view.

Additionally, an interface for navigating this API will be very useful. Graphene
includes the [graphiql](https://github.com/graphql/graphiql) in-browser IDE
which assists in exploring and querying your new API. We’ll add a URL for this too.

```python
from django.conf.urls import url, include
from django.views.decorators.csrf import csrf_exempt
from graphene.contrib.django.views import GraphQLView
from quickstart.schema import schema


# Wire up our GraphQL schema to /graphql.
# Additionally, we include GraphiQL view for querying easily our schema.
urlpatterns = [
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(schema=schema))),
    url(r'^graphiql', include('django_graphiql.urls')),
]
```

## Testing our GraphQL schema

We're now ready to test the API we've built. Let's fire up the server from the command line.

```bash
python ./manage.py runserver
```

Go to [localhost:8080/graphiql](http://localhost:8080/graphiql) and type your first query!

```graphql
myQuery {
    getUser(id:"1") {
        username
    }
}
```
