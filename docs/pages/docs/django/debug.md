---
title: Django Debug Middleware
description: How to debug Django queries and requests using Graphene
---

# Django Debug Middleware

You can debug your GraphQL queries in a similar way to [django-debug-toolbar](https://django-debug-toolbar.readthedocs.org/),
but outputing in the results in GraphQL response as fields, instead of the graphical HTML interface.


For that, you will need to add the plugin in your graphene schema.

## Installation

For use the Django Debug plugin in Graphene:
* Import `DjangoDebugMiddleware` and add it to the `middlewares` argument when you initiate the `Schema`.
* Add the `debug` field into the schema root `Query` with the value `graphene.Field(DjangoDebug, name='__debug')`.


```python
from graphene.contrib.django.debug import DjangoDebugMiddleware, DjangoDebug

class Query(graphene.ObjectType):
    # ...
    debug = graphene.Field(DjangoDebug, name='__debug')

schema = graphene.Schema(query=Query, middlewares=[DjangoDebugMiddleware()])
```


## Querying

You can query it for outputing all the sql transactions that happened in the GraphQL request, like:

```graphql
{
  # A example that will use the ORM for interact with the DB
  allIngredients {
    edges {
      node {
        id,
        name
      }
    }
  }
  # Here is the debug field that will output the SQL queries
  __debug {
    sql {
      rawSql
    }
  }
}
```
Note that the `__debug` field must be the last field in your query.
