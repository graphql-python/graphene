---
title: Mutations
description: Walkthrough Mutations
---

# Mutations

A Mutation is a special ObjectType that also defines an Input.

## Quick example

This example defines a Mutation:

```python
import graphene

class CreatePerson(graphene.Mutation):
    class Input:
        name = graphene.String()

    ok = graphene.Boolean()
    person = graphene.Field('Person')

    @classmethod
    def mutate(cls, instance, args, info):
        person = Person(name=args.get('name'))
        ok = True
        return CreatePerson(person=person, ok=ok)
```

**person** and **ok** are the output fields of the Mutation when is resolved.

**Input** attributes are the arguments that the Mutation `CreatePerson` needs for resolving, in this case **name** will be the only argument for the mutation.

**mutate** is the function that will be applied once the mutation is called.

So, we can finish our schema like this:

```python
# ... the Mutation Class

class Person(graphene.ObjectType):
    name = graphene.String()

class MyMutations(graphene.ObjectType):
    create_person = graphene.Field(CreatePerson)

schema = graphene.Schema(mutation=MyMutations)
```

## Executing the Mutation

Then, if we query (`schema.execute(query_str)`) the following:
```graphql
mutation myFirstMutation {
    createPerson(name:"Peter") {
        person {
            name
        }
        ok
    }
}
```

We should receive:

```json
{
    "createPerson": {
        "person" : {
            name: "Peter"
        },
        "ok": true
    }
}
