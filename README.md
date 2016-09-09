You are in the `next` unreleased version of Graphene (`1.0.dev`).
Please read [UPGRADE-v1.0.md](/UPGRADE-v1.0.md) to learn how to upgrade.

---

# ![Graphene Logo](http://graphene-python.org/favicon.png) [Graphene](http://graphene-python.org) [![Build Status](https://travis-ci.org/graphql-python/graphene.svg?branch=master)](https://travis-ci.org/graphql-python/graphene) [![PyPI version](https://badge.fury.io/py/graphene.svg)](https://badge.fury.io/py/graphene) [![Coverage Status](https://coveralls.io/repos/graphql-python/graphene/badge.svg?branch=master&service=github)](https://coveralls.io/github/graphql-python/graphene?branch=master)


[Graphene](http://graphene-python.org) is a Python library for building GraphQL schemas/types fast and easily.

- **Easy to use:** Graphene helps you use GraphQL in Python without effort.
- **Relay:** Graphene has builtin support for Relay
- **Django:** Automatic *Django model* mapping to Graphene Types. Check a fully working [Django](http://github.com/graphql-python/swapi-graphene) implementation

Graphene also supports *SQLAlchemy*!

*What is supported in this Python version?* **Everything**: Interfaces, ObjectTypes, Scalars, Unions and Relay (Nodes, Connections), in addition to queries, mutations and subscriptions.

**NEW**!: [Try graphene online](http://graphene-python.org/playground/)

## Installation

For instaling graphene, just run this command in your shell

```bash
pip install graphene
# In case of need Django model support
pip install graphene[django]
# Or in case of need SQLAlchemy support
pip install graphene[sqlalchemy]
```

## 1.0 Upgrade Guide

Please read [UPGRADE-v1.0.md](/UPGRADE-v1.0.md) to learn how to upgrade.


## Examples

Here is one example for get you started:

```python
class Query(graphene.ObjectType):
    hello = graphene.String(description='A typical hello world')
    ping = graphene.String(description='Ping someone',
                           to=graphene.String())

    def resolve_hello(self, args, info):
        return 'World'

    def resolve_ping(self, args, info):
        return 'Pinging {}'.format(args.get('to'))

schema = graphene.Schema(query=Query)
```

Then Querying `graphene.Schema` is as simple as:

```python
query = '''
    query SayHello {
      hello
      ping(to:"peter")
    }
'''
result = schema.execute(query)
```

If you want to learn even more, you can also check the following [examples](examples/):

* **Basic Schema**: [Starwars example](examples/starwars)
* **Relay Schema**: [Starwars Relay example](examples/starwars_relay)
* **Django model mapping**: [Starwars Django example](examples/starwars_django)
* **SQLAlchemy model mapping**: [Flask SQLAlchemy example](examples/flask_sqlalchemy)


## Contributing

After cloning this repo, ensure dependencies are installed by running:

```sh
python setup.py install
```

After developing, the full test suite can be evaluated by running:

```sh
python setup.py test # Use --pytest-args="-v -s" for verbose mode
```
