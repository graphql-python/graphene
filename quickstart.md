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

First we're going to define some GraphQL ObjectTypes for our `Schema`:


```python
import graphene

schema = graphene.Schema()

# This will be our root query
class Query(graphene.ObjectType):
    username = graphene.StringField(description='The username')

   	def resolve_username(self, *args):
   		return 'Hello World'

# Here we set the root query for our schema
schema.query = Query
```

Then, we can start querying our schema:

```python
result = schema.execute('{ username }')

# result.data should be {'username': 'Hello World'}
username = result.data['username']

print(username)
```

Congrats! You got your first version of graphene working!

**This Quickstart page needs to be improved, meanwhile visit the [schema](https://github.com/graphql-python/django-graphene-example/blob/master/starwars/schema.py) of our Starwars Django example!**
