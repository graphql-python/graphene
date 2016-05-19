---
title: Resolvers
description: Walkthrough Resolvers
---

# Resolvers

A resolver is a method that resolves certain field within a `ObjectType`.
The resolver of a field will be, if not specified otherwise, the `resolve_{field_name}` within the `ObjectType`.

By default a resolver will take the `args`, and `info` arguments.
*This is likely to be simplified in the future*.


## Quick example

This example model defines a `Query` type, which has a reverse field that reverses the given `word`
argument using the `resolve_reverse` method in the class.

```python
import graphene

class Query(graphene.ObjectType):
    reverse = graphene.String(word=graphene.String())

    def resolve_reverse(self, args, info):
        word = args.get('word')
        return word[::-1]
```

## Resolvers outside the class

A field could also specify a custom resolver outside the class:

```python
import graphene

def reverse(root, args, info):
    word = args.get('word')
    return word[::-1]

class Query(graphene.ObjectType):
    reverse = graphene.String(word=graphene.String(), resolver=reverse)
```


## Context

A query in a GraphQL schema could have some context that we can use in any resolver.
In this case we need to decorate the resolver function with `with_context`.

```python
class Query(graphene.ObjectType):
    name = graphene.String()

    @with_context
    def resolve_name(self, args, context, info):
        return context['name']


result = schema.execute(query, context_value={'name': 'Peter'})
```
