---
title: ObjectTypes
description: Walkthrough ObjectTypes
---

# ObjectTypes

An ObjectType is the single, definitive source of information about your data. It contains the essential fields and behaviors of the data you’re querying.

The basics:
- Each ObjectType is a Python class that inherits graphene.ObjectType or inherits an implemented [Interface](/docs/interfaces/).
- Each attribute of the ObjectType represents a GraphQL field.

## Quick example

This example model defines a Person, which has a first_name and last_name:

```python
import graphene

class Person(graphene.ObjectType):
    first_name = graphene.String()
    last_name = graphene.String()
    full_name = graphene.String()

    def resolve_full_name(self, args, info):
        return '{} {}'.format(self.first_name, self.last_name)
```

**first_name** and **last_name** are fields of the ObjectType. Each field is specified as a class attribute, and each attribute maps to a GraphQL field.

The above `Person` ObjectType would have the following representation in a schema:

```graphql
type Person {
  firstName: String
  lastName: String
  fullName: String
}
```

## Instances as containers

Graphene `ObjectType`s could act as containers too.
So with the previous example you could do.

```python
peter = Person(first_name='Peter', last_name='Griffin')
```