---
title: Enums
description: Walkthrough Enums
---

# Enums

A `Enum` is a special `GraphQL` type that represents a set of symbolic names (members) bound to unique, constant values.

## Enum definition

You can create an `Enum` using classes:

```python
import graphene

class Episode(graphene.Enum):
    NEWHOPE = 4
    EMPIRE = 5
    JEDI = 6
```

But also using instances of Enum:

```python
Episode = graphene.Enum('Episode', [('NEWHOPE', 4), ('EMPIRE', 5), ('JEDI', 6)])
```

## Notes

Internally, `graphene.Enum` uses [`enum.Enum`](https://docs.python.org/3/library/enum.html) Python implementation if available, or a backport if not.

So you can use it in the same way as you would do with Python `enum.Enum`.
