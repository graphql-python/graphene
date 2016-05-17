---
title: Getting started
description: A Quick guide to Graphene
---

# Getting started

Let's build a basic GraphQL schema from scratch.


## Requirements

- Python (2.6.5+, 2.7, 3.2, 3.3, 3.4, 3.5, pypy)
- Graphene (0.4+)


## Project setup

```bash
pip install graphene
```

## Creating a basic Schema

A GraphQL schema describes your data model, and provides a GraphQL server with an associated set of resolve methods that know how to fetch data.

We are going to create a very simple schema, with a `Query` with only one field: `hello`. And when we query it should return `"World"`.


```python
import graphene

class Query(graphene.ObjectType):
    hello = graphene.String()

    def resolve_hello(self, args, context, info):
        return 'World'

schema = graphene.Schema(query=Query)
```


## Querying

Then, we can start querying our schema:

```python
result = schema.execute('{ hello }')
print result.data['hello'] # "World"
```

Congrats! You got your first graphene schema working!
