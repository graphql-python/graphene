---
title: Basic Types
description: Walkthrough Basic Types
---

# Basic Types

Graphene define the following base Types:
- `graphene.String`
- `graphene.Int`
- `graphene.Float`
- `graphene.Boolean`
- `graphene.ID`

Also, define:
- `graphene.List`
- `graphene.NonNull`

## Mounting in ClassTypes

This types if are mounted in a `ObjectType`, `Interface` or `Mutation`,
 would act as `Field`s.
So, the following examples will behave exactly the same:

```python
class Person(graphene.ObjectType):
    name = graphene.String()
```
and

```python
class Person(graphene.ObjectType):
    name = graphene.Field(graphene.String())
```

## Mounting in Fields

If this types are mounted in a `Field`, would act as `Argument`s.
So, the following examples will behave exactly the same:

```python
class Person(graphene.ObjectType):
    say_hello = graphene.Field(graphene.String(),
                               to=graphene.String())
```
and

```python
class Person(graphene.ObjectType):
    say_hello = graphene.Field(graphene.String(),
                               to=graphene.Argument(graphene.String()))
```
