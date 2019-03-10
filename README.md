**We are looking for contributors**! Please check the [ROADMAP](https://github.com/graphql-python/graphene/blob/master/ROADMAP.md) to see how you can help ❤️

---

# ![Graphene Logo](http://graphene-python.org/favicon.png) [Graphene](http://graphene-python.org) [![Build Status](https://travis-ci.org/graphql-python/graphene.svg?branch=master)](https://travis-ci.org/graphql-python/graphene) [![PyPI version](https://badge.fury.io/py/graphene.svg)](https://badge.fury.io/py/graphene) [![Coverage Status](https://coveralls.io/repos/graphql-python/graphene/badge.svg?branch=master&service=github)](https://coveralls.io/github/graphql-python/graphene?branch=master)

<h1 align="center">Supporting Graphene Python</h1>

Graphene is an MIT-licensed open source project. It's an independent project with its ongoing development made possible entirely thanks to the support by these awesome [backers](https://github.com/graphql-python/graphene/blob/master/BACKERS.md). If you'd like to join them, please consider:

- [Become a backer or sponsor on Patreon](https://www.patreon.com/syrusakbary).
- [One-time donation via PayPal.](https://graphene-python.org/support-graphene/)

<!--<h2 align="center">Special Sponsors</h2>


<p align="center">
  <a href="https://stdlib.com" target="_blank">
    <img width="260px" src="https://raw.githubusercontent.com/graphql-python/graphene-python.org/master/src/pages/sponsors/generic-logo.png">
  </a>
</p>

<!--special end-->

<h2 align="center">Platinum via Patreon</h2>

<!--platinum start-->
<table>
  <tbody>
    <tr>
      <td align="center" valign="middle">
        <a href="https://www.patreon.com/join/syrusakbary" target="_blank">
          <img width="222px" src="https://raw.githubusercontent.com/graphql-python/graphene-python.org/master/src/pages/sponsors/generic-logo.png">
        </a>
      </td>
    </tr>
  </tbody>
</table>

<h2 align="center">Gold via Patreon</h2>

<!--gold start-->
<table>
  <tbody>
    <tr>
      <td align="center" valign="middle">
        <a href="https://www.patreon.com/join/syrusakbary" target="_blank">
          <img width="148px" src="https://raw.githubusercontent.com/graphql-python/graphene-python.org/master/src/pages/sponsors/generic-logo.png">
        </a>
      </td>
    </tr>
  </tbody>
</table>
<!--gold end-->

<h2 align="center">Silver via Patreon</h2>

<!--silver start-->
<table>
  <tbody>
    <tr>
      <td align="center" valign="middle">
        <a href="https://www.patreon.com/join/syrusakbary" target="_blank">
          <img width="148px" src="https://raw.githubusercontent.com/graphql-python/graphene-python.org/master/src/pages/sponsors/generic-logo.png">
        </a>
      </td>
    </tr>
  </tbody>
</table>
<!--silver end-->

---

## Introduction

[Graphene](http://graphene-python.org) is a Python library for building GraphQL schemas/types fast and easily.

- **Easy to use:** Graphene helps you use GraphQL in Python without effort.
- **Relay:** Graphene has builtin support for Relay.
- **Data agnostic:** Graphene supports any kind of data source: SQL (Django, SQLAlchemy), NoSQL, custom Python objects, etc.
  We believe that by providing a complete API you could plug Graphene anywhere your data lives and make your data available
  through GraphQL.

## Integrations

Graphene has multiple integrations with different frameworks:

| integration       | Package                                                                                 |
| ----------------- | --------------------------------------------------------------------------------------- |
| Django            | [graphene-django](https://github.com/graphql-python/graphene-django/)                   |
| SQLAlchemy        | [graphene-sqlalchemy](https://github.com/graphql-python/graphene-sqlalchemy/)           |
| Google App Engine | [graphene-gae](https://github.com/graphql-python/graphene-gae/)                         |
| Peewee            | _In progress_ ([Tracking Issue](https://github.com/graphql-python/graphene/issues/289)) |

Also, Graphene is fully compatible with the GraphQL spec, working seamlessly with all GraphQL clients, such as [Relay](https://github.com/facebook/relay), [Apollo](https://github.com/apollographql/apollo-client) and [gql](https://github.com/graphql-python/gql).

## Installation

For instaling graphene, just run this command in your shell

```bash
pip install "graphene>=2.0"
```

## 2.0 Upgrade Guide

Please read [UPGRADE-v2.0.md](/UPGRADE-v2.0.md) to learn how to upgrade.

## Examples

Here is one example for you to get started:

```python
class Query(graphene.ObjectType):
    hello = graphene.String(description='A typical hello world')

    def resolve_hello(self, info):
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

- **Basic Schema**: [Starwars example](examples/starwars)
- **Relay Schema**: [Starwars Relay example](examples/starwars_relay)

## Documentation

Documentation and links to additional resources are available at
https://docs.graphene-python.org/en/latest/

## Contributing

After cloning this repo, create a [virtualenv](https://virtualenv.pypa.io/en/stable/) and ensure dependencies are installed by running:

```sh
virtualenv venv
source venv/bin/activate
pip install -e ".[test]"
```

Well-written tests and maintaining good test coverage is important to this project. While developing, run new and existing tests with:

```sh
py.test graphene/relay/tests/test_node.py # Single file
py.test graphene/relay # All tests in directory
```

Add the `-s` flag if you have introduced breakpoints into the code for debugging.
Add the `-v` ("verbose") flag to get more detailed test output. For even more detailed output, use `-vv`.
Check out the [pytest documentation](https://docs.pytest.org/en/latest/) for more options and test running controls.

You can also run the benchmarks with:

```sh
py.test graphene --benchmark-only
```

Graphene supports several versions of Python. To make sure that changes do not break compatibility with any of those versions, we use `tox` to create virtualenvs for each python version and run tests with that version. To run against all python versions defined in the `tox.ini` config file, just run:

```sh
tox
```

If you wish to run against a specific version defined in the `tox.ini` file:

```sh
tox -e py36
```

Tox can only use whatever versions of python are installed on your system. When you create a pull request, Travis will also be running the same tests and report the results, so there is no need for potential contributors to try to install every single version of python on their own system ahead of time. We appreciate opening issues and pull requests to make graphene even more stable & useful!

### Building Documentation

The documentation is generated using the excellent [Sphinx](http://www.sphinx-doc.org/) and a custom theme.

An HTML version of the documentation is produced by running:

```sh
make docs
```
