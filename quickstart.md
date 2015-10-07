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

First we're going to define some GraphQL ObjectTypes that we'll use in our `Schema`:

```
import graphene

```