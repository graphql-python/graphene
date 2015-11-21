---
title: Django Quickstart Guide
active_tab: quickstart
description: A Quick guide to Graphene in Django
---

## Django Quickstart

In our previous quickstart page we created a very simple schema.
Now we will adapt the schema for our Django models.

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
cd tutorial
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

Right, we'd better write some types then. Open `tutorial/quickstart/schema.py` and get typing.

```python
import graphene
from graphene.contrib.django import DjangoObjectType

from django.contrib.auth.models import User, Group

# Graphene will map automaticall the User model to UserType with
# the specified fields
class UserType(DjangoObjectType):
    class Meta:
        model = User
        only_fields = ('username', 'email', 'groups')


class GroupType(DjangoObjectType):
    class Meta:
        model = User
        only_fields = ('name', )


class Query(graphene.ObjectType):
    all_users = graphene.List(UserType)
    get_user = graphene.Field(UserType
                              id=graphene.String(required=True))

    def resolve_all_users(self, args, info):
        return User.objects.all()

    def resolve_get_user(self, args, info):
        return User.objects.get(id=args.get('id'))

schema = graphene.Schema(query=Query)
```


## Creating GraphQL and GraphiQL views

Okay, now let's wire up the GraphQL and GraphiQL urls. On to `tutorial/urls.py`...


```python
from django.conf.urls import url, include
from django.views.decorators.csrf import csrf_exempt
from graphene.contrib.django.views import GraphQLView
from tutorial.quickstart.schema import schema


# Wire up our GraphQL schema in /graphql.
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
