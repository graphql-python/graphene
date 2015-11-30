---
title: Django Tutorial
description: A Quick guide to Graphene in Django
---

# Django Tutorial

In our previous quickstart page we created a very simple schema.

Now we will adapt the schema to automatically map some Django models,
and expose this schema in a `/graphql` API endpoint.

## Project setup

```bash
# Create the project directory
mkdir tutorial
cd tutorial

# Create a virtualenv to isolate our package dependencies locally
virtualenv env
source env/bin/activate  # On Windows use `env\Scripts\activate`

# Install Django and Graphene with Django support
pip install django
pip install graphene[django]
pip install django-graphiql

# Set up a new project with a single application
django-admin.py startproject tutorial .  # Note the trailing '.' character
django-admin.py startapp quickstart
```

Now sync your database for the first time:

```bash
python manage.py migrate
```

We'll also create an initial user named `admin` with a password of `password`.

```bash
python manage.py createsuperuser
```

Once you've set up a database and initial user created and ready to go, open up the app's directory and we'll get coding...



## Schema

GraphQL presents your objects to the world as a graph structure rather than a more
heiricarcal structure to which you may be acustomed. In order to create this
representation, Graphene needs to know about each *type* of object which will appear in
the graph. Below we define these as the `UserType` and `GroupType` classes.

This graph also has a 'root' through which all access begins. This is the `Query` class below.
In this example, we provide the ability to list all users via `all_users`, and the
ability to obtain a single user via `get_user`.

Open `tutorial/quickstart/schema.py` and type the following:

```python
import graphene
from graphene.contrib.django import DjangoObjectType

from django.contrib.auth.models import User, Group

# Graphene will automatically map the User model's fields onto the UserType.
# This is configured in the UserType's Meta class
class UserType(DjangoObjectType):
    class Meta:
        model = User
        only_fields = ('username', 'email', 'groups')


class GroupType(DjangoObjectType):
    class Meta:
        model = Group
        only_fields = ('name', )


class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    get_user = graphene.Field(UserType,
                              id=graphene.String().NonNull)
    get_group = graphene.Field(GroupType,
                               id=graphene.String().NonNull)

    def resolve_all_users(self, args, info):
        return User.objects.all()

    def resolve_get_user(self, args, info):
        return User.objects.get(id=args.get('id'))

    def resolve_get_group(self, args, info):
        return Group.objects.get(id=args.get('id'))

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

Additionally, and interface for navigating this API will be very useful. Graphene
includes the [graphiql](https://github.com/graphql/graphiql) in-browser IDE
which assits and exploring and querying your new API. We'll add a URL for this too.

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
