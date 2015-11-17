---
layout: page
title: Quickstart Guide
active_tab: quickstart
description: A Quick guide to Graphene
---

Graphene is a powerful framework for creating GraphQL schemas easily in Python.

## Requirements

- Python (2.6.5+, 2.7, 3.2, 3.3, 3.4, 3.5, pypy)
- Graphene (0.1+)

The following packages are optional:

- Django (1.6+)


## Project setup

```bash
# Create the project directory
mkdir tutorial
cd tutorial

# Create a virtualenv to isolate our package dependencies locally
virtualenv env
source env/bin/activate  # On Windows use `env\Scripts\activate`

pip install graphene
```

## Types

First we're going to define some GraphQL ObjectTypes and relay Nodes for our `Schema`:


```python
import graphene
from graphene import relay
from somewhere import (fetch_user_from_database, fetch_users_from_database)

schema = graphene.Schema()

class User(relay.Node):
    """A User fetched from the database"""
    user_id = graphene.ID()
    first_name = graphene.String()
    last_name = graphene.String()
    full_name = graphene.String(description='A field created by setting the first and last name.')
    email_address = graphene.String()
    age = graphene.Int()

    @classmethod
    def get_node(cls, user_id):
        user_dict = fetch_user_from_database(user_id)
        # user_dict will contain the fields, user_id, first_name, last_name, email_address and age
        user_dict['id'] = user_dict['user_id'] # will be used to set the global ID used by relay
        return User(**user_dict)

    def resolve_full_name(self, *args):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        return None

def _create_relay_user(user):
    # user_dict will contain the fields, user_id, first_name, last_name, email_address and age
    user['id'] = user['user_id']
    return User(**user)

# This will be our root query
class Query(graphene.ObjectType):
        users = graphene.List(User,
                            userName=graphene.Argument(graphene.String),
                            sortKey=graphene.Argument(graphene.String),
                            sortDirection=graphene.Argument(graphene.String))
        user = relay.NodeField(Users)
        viewer = graphene.Field('self') # needed for Relay
        
        # args will be a dict with 'userName', 'sortKey' and 'sortDirection'
        # info is an object with information about the query being sent
        def resolve_users(self, args, info):
            list_of_user_dicts = fetch_users_from_database(args)
            return [_create_relay_user(user) for user in list_of_user_dicts]

        def resolve_viewer(self, *args, **kwargs):
            return self

# Here we set the root query for our schema
schema.query = Query
```

Then, we can start querying our schema:

```python
result = schema.execute('query { users { fullName } }')

# result.data should be {'users': [{fullName: 'Provided Name'}]}
users = result.data['users']

print(users)
```

Congrats! You got your first version of graphene working!

**This Quickstart page needs to be improved, meanwhile visit the [schema](https://github.com/graphql-python/django-graphene-example/blob/master/starwars/schema.py) of our Starwars Django example!**
