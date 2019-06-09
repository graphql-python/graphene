# Graphene Roadmap

In order to move Graphene and the GraphQL Python ecosystem forward I realized is essential to be clear with the community on next steps, so we can move uniformly.

There are few key points that need to happen in the short/mid term, divided into two main sections:

- [Community](#community)
- [Graphene 3](#graphene-3)

_👋 If you have more ideas on how to move the Graphene ecosystem forward, don't hesistate to [open a PR](https://github.com/graphql-python/graphene/edit/master/ROADMAP.md)_

## Community

The goal is to improve adoption and sustainability of the project.

- 💎 Add Commercial Support for Graphene - [See issue](https://github.com/graphql-python/graphene/issues/813)
  - Create [Patreon page](https://www.patreon.com/syrusakbary)
  - Add [/support-graphene page](https://graphene-python.org/support-graphene/) in Graphene website
- 📘 Vastly improve documentation - [See issue](https://github.com/graphql-python/graphene/issues/823)

## Graphene 3

The goal is to summarize the different improvements that Graphene will need to accomplish for version 3.

In a nushell, Graphene 3 should take the Python 3 integration one step forward while still maintaining compatibility with Python 2.

- 🚀 [graphql-core-next](https://github.com/graphql-python/graphql-core-next) GraphQL engine support (almost same API as graphql-core)
- 🔸 GraphQL types from type annotations - [See issue](https://github.com/graphql-python/graphene/issues/729)
- 📄 Schema creation from SDL (API TBD)
- ✨ Improve connections structure
- 📗 Improve function documentation
- 🔀 Add support for coroutines in Connection, Mutation (abstracting out Promise requirement) - [See PR](https://github.com/graphql-python/graphene/pull/824)
