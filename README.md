You are in the `next` unreleased version of Graphene (`1.0.dev`).
Please read [UPGRADE-v1.0.md](/UPGRADE-v1.0.md) to learn how to upgrade.

---

# ![Graphene Logo](http://graphene-python.org/favicon.png) [Graphene](http://graphene-python.org) [![Build Status](https://travis-ci.org/graphql-python/graphene.svg?branch=master)](https://travis-ci.org/graphql-python/graphene) [![PyPI version](https://badge.fury.io/py/graphene.svg)](https://badge.fury.io/py/graphene) [![Coverage Status](https://coveralls.io/repos/graphql-python/graphene/badge.svg?branch=master&service=github)](https://coveralls.io/github/graphql-python/graphene?branch=master)


[Graphene](http://graphene-python.org) is a Python library for building GraphQL schemas/types fast and easily.

- **Easy to use:** Graphene helps you use GraphQL in Python without effort.
- **Relay:** Graphene has builtin support for Relay
- **Data agnostic:** Graphene supports any kind of data source: SQL (Django, SQLAlchemy), NoSQL, custom Python objects...
  We believe that by providing a complete API you could plug Graphene anywhere your data lives and make your data available
  through GraphQL.


## Integrations

Graphene has multiple integrations with different frameworks:

| integration   |   Package |
|---------------|-------------------|
| Django        |  [graphene-django](https://github.com/graphql-python/graphene-django/)  |
| SQLAlchemy    |  [graphene-sqlalchemy](https://github.com/graphql-python/graphene-sqlalchemy/)  |
| Google App Engine    |  [graphene-gae](https://github.com/graphql-python/graphene-gae/)  |
| Peewee    |  *In progress* ([Tracking Issue](https://github.com/graphql-python/graphene/issues/289))  |


## Installation

For instaling graphene, just run this command in your shell

```bash
pip install "graphene>=1.0.dev"
```

## 1.0 Upgrade Guide

Please read [UPGRADE-v1.0.md](/UPGRADE-v1.0.md) to learn how to upgrade.


## Examples

Here is one example for get you started:

```python
class Query(graphene.ObjectType):
    hello = graphene.String(description='A typical hello world')

    def resolve_hello(self, args, context, info):
        return 'World'

schema = graphene.Schema(query=Query)
```

Then Querying `graphene.Schema` is as simple as:

```python
query = '''
    query SayHello {
      hello
    }
'''
result = schema.execute(query)
```

If you want to learn even more, you can also check the following [examples](examples/):

* **Basic Schema**: [Starwars example](examples/starwars)
* **Relay Schema**: [Starwars Relay example](examples/starwars_relay)


## Contributing

After cloning this repo, ensure dependencies are installed by running:

```sh
python setup.py install
```

After developing, the full test suite can be evaluated by running:

```sh
python setup.py test # Use --pytest-args="-v -s" for verbose mode
```
