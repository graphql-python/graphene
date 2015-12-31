---
title: Django Quickstart
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

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=100)
    notes = models.TextField()
    category = models.ForeignKey(Category, related_name='ingredients')

    def __str__(self):
        return self.name
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
from graphene import relay, ObjectType
from graphene.contrib.django.filter import DjangoFilterConnectionField
from graphene.contrib.django.types import DjangoNode

from cookbook.ingredients.models import Category, Ingredient


# Graphene will automatically map the User model's fields onto the UserType.
# This is configured in the UserType's Meta class (as you can see below)
class CategoryNode(DjangoNode):
    class Meta:
        model = Category
        filter_fields = ['name', 'ingredients']
        filter_order_by = ['name']


class IngredientNode(DjangoNode):
    class Meta:
        model = Ingredient
        # Allow for some more advanced filtering here
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'notes': ['exact', 'icontains'],
            'category': ['exact'],
            'category__name': ['exact'],
        }
        filter_order_by = ['name', 'category__name']


class Query(ObjectType):
    category = relay.NodeField(CategoryNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)

    ingredient = relay.NodeField(IngredientNode)
    all_ingredients = DjangoFilterConnectionField(IngredientNode)

    class Meta:
        abstract = True
```

The filtering functionality is provided by
[django-filter](https://django-filter.readthedocs.org). See the
[usage documentation](https://django-filter.readthedocs.org/en/latest/usage.html#the-filter)
for details on the format for `filter_fields`.

Note that the above `Query` class is marked as 'abstract'. This is because we
want will now create a project-level query which will combine all our app-level
queries.

Create the parent project-level `cookbook/schema.py`:

```python
import graphene

import cookbook.ingredients.schema


class Query(cookbook.ingredients.schema.Query):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

schema = graphene.Schema(name='Cookbook Schema')
schema.query = Query
```

You can think of this as being something like your top-level `urls.py`
file (although it currently lacks any namespacing).

## Adding GraphiQL

GraphiQL is a web-based integrated development environment to assist in the
writing and executing of GraphQL queries. It will provide us with a simple
and easy way of testing our cookbook project.

Add `django_graphiql` to `INSTALLED_APPS` in `cookbook/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'django_graphiql',
]
```

## Creating GraphQL and GraphiQL views

Unlike a RESTful API, there is only a single URL from which GraphQL is accessed.
Requests to this URL are handled by Graphene's `GraphQLView` view.

Additionally, we'll add a URL for aforementioned GraphiQL, and for the Django admin
interface (the latter can be useful for creating test data).

```python
from django.conf.urls import url, include
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt

from graphene.contrib.django.views import GraphQLView

from cookbook.schema import schema

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^graphql', csrf_exempt(GraphQLView.as_view(schema=schema))),
    url(r'^graphiql', include('django_graphiql.urls')),
]
```

## Load some test data

Now is a good time to load up some test data. The easiest option will be to
[download the ingredients.json](https://raw.githubusercontent.com/graphql-python/graphene/feature/django/examples/cookbook/cookbook/ingredients/fixtures/ingredients.json)
fixture and place it in
`cookbook/ingredients/fixtures/ingredients.json`. You can then run the following:

```
$ python ./manage.py loaddata ingredients

Installed 6 object(s) from 1 fixture(s)
```

Alternatively you can use the Django admin interface to create some data youself.
You'll need to run the development server (see below), and probably create a login
for yourself too (`./manage.py createsuperuser`).

## Testing our GraphQL schema

We're now ready to test the API we've built. Let's fire up the server from the command line.

```bash
$ python ./manage.py runserver

Performing system checks...
Django version 1.9, using settings 'cookbook.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

Go to [localhost:8000/graphiql](http://localhost:8000/graphiql) and type your first query!

```graphql
query {
  allIngredients {
    edges {
      node {
        id,
        name
      }
    }
  }
}
```

The above will return the names & IDs for all ingredients. But perhaps you want
a specific ingredient:

```graphql
query {
  # Graphene creates globally unique IDs for all objects.
  # You may need to copy this value from the results of the first query
  ingredient(id: "SW5ncmVkaWVudE5vZGU6MQ==") {
    name
  }
}
```

You can also get each ingredient for each category:

```graphql
query {
  allCategories {
    edges {
      node {
        name,

        ingredients {
          edges {
            node {
              name
}}}}}}}
```

Or you can get only 'meat' ingredients containing the letter 'e':

```graphql
query {
  # You can also use `category: "CATEGORY GLOBAL ID"`
  allIngredients(nameIcontains: "e", categoryName: "Meat") {
    edges {
      node {
        name
}}}}
```
