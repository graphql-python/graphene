---
title: Basic Types
description: Walkthrough Basic Types
---

# Basic Types

Graphene define the following base Scalar Types:
- `graphene.String`
- `graphene.Int`
- `graphene.Float`
- `graphene.Boolean`
- `graphene.ID`

Also the following Types are available:
- `graphene.List`
- `graphene.NonNull`

## Shorcuts

There are some shorcuts for code easier.
The following are equivalent

```python
# A list of strings
string_list = graphene.List(graphene.String())
string_list = graphene.String().List

# A non-null string
string_non_null = graphene.String().NonNull
string_non_null = graphene.NonNull(graphene.String())
```


## Custom scalars

You can also create a custom scalar for your schema.
If you want to create a DateTime Scalar Type just type:

```python
import datetime
from graphql.core.language import ast

class DateTime(Scalar):
    '''DateTime'''
    @staticmethod
    def serialize(dt):
        return dt.isoformat()

    @staticmethod
    def parse_literal(node):
        if isinstance(node, ast.StringValue):
            return datetime.datetime.strptime(
                node.value, "%Y-%m-%dT%H:%M:%S.%f")

    @staticmethod
    def parse_value(value):
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
```

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
graphene.Field(graphene.String(), to=graphene.String())
```
and

```python
graphene.Field(graphene.String(), to=graphene.Argument(graphene.String()))
```
