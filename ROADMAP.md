# GraphQL Python Roadmap

In order to move Graphene and the GraphQL Python ecosystem forward it's essential to be clear with the community on next steps, so we can move uniformly.

_👋 If you have more ideas on how to move the Graphene ecosystem forward, don't hesistate to [open a PR](https://github.com/graphql-python/graphene/edit/master/ROADMAP.md)_


## Now
- [ ] Continue to support v2.x with security releases
- [ ] Last major/feature release is cut and graphene-* libraries should pin to that version number

## Next
New features will only be developed on version 3 of ecosystem libraries.

### [Core-Next](https://github.com/graphql-python/graphql-core-next)
Targeted as v3 of [graphql-core](https://pypi.org/project/graphql-core/), Python 3 only

### Graphene
- [ ] Integrate with the core-next API and resolve all breaking changes
- [ ] GraphQL types from type annotations - [See issue](https://github.com/graphql-python/graphene/issues/729)
- [ ] Add support for coroutines in Connection, Mutation (abstracting out Promise requirement) - [See PR](https://github.com/graphql-python/graphene/pull/824)

### Graphene-*
- [ ] Integrate with the graphene core-next API and resolve all breaking changes

### *-graphql
- [ ] Integrate with the graphql core-next API and resolve all breaking changes

## Ongoing Initiatives
- [ ] Improve documentation, especially for new users to the library
- [ ] Recipes for “quick start” that people can ideally use/run


## Dependent Libraries
| Repo                                                                         | Release Manager | CODEOWNERS | Pinned     | next/master created | Labels Standardized |
| ---------------------------------------------------------------------------- | --------------- | ---------- | ---------- | ------------------- | ------------------- |
| [graphene](https://github.com/graphql-python/graphene)                       | ekampf          | ✅          |            | ✅                   |                     |
| [graphql-core](https://github.com/graphql-python/graphql-core)               | Cito            | ✅          | N/A        | N/A                 |                     |
| [graphql-core-next](https://github.com/graphql-python/graphql-core-next)     | Cito            | ✅          | N/A        | N/A                 |                     |
| [graphql-server-core](https://github.com/graphql-python/graphql-server-core) | Cito            |            | ✅          | ✅                   |                     |
| [gql](https://github.com/graphql-python/gql)                                 | ekampf          |            |            |                     |                     |
| [gql-next](https://github.com/graphql-python/gql-next)                       | ekampf          |            | N/A        | N/A                 |                     |
| ...[aiohttp](https://github.com/graphql-python/aiohttp-graphql)              |                 |            |            |                     |                     |
| ...[django](https://github.com/graphql-python/graphene-django)               | mvanlonden      |            | ✅          | ✅                   |                     |
| ...[sanic](https://github.com/graphql-python/sanic-graphql)                  | ekampf          |            |            |                     |                     |
| ...[flask](https://github.com/graphql-python/flask-graphql)                  |                 |            |            |                     |                     |
| ...[webob](https://github.com/graphql-python/webob-graphql)                  |                 |            |            |                     |                     |
| ...[tornado](https://github.com/graphql-python/graphene-tornado)             | ewhauser        |            | PR created | ✅                   |                     |
| ...[ws](https://github.com/graphql-python/graphql-ws)                        | Cito/dfee       |            | ✅          | ✅                   |                     |
| ...[gae](https://github.com/graphql-python/graphene-gae)                     | ekampf          |            | PR created | ✅                   |                     |
| ...[sqlalchemy](https://github.com/graphql-python/graphene-sqlalchemy)       | jnak/Nabell     | ✅          | ✅          | ✅                   |                     |
| ...[mongo](https://github.com/graphql-python/graphene-mongo)                 |                 |            | ✅          | ✅                   |                     |
| ...[relay-py](https://github.com/graphql-python/graphql-relay-py)            | Cito            |            |            |                     |                     |
| ...[wsgi](https://github.com/moritzmhmk/wsgi-graphql)                        |                 |            |            |                     |                     |
