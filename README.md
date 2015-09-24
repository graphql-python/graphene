# Graphene: GraphQL Object Mapper

This is a library to use GraphQL in Python in a easy way.
It will map the models/fields to internal GraphQL-py objects without effort.

[![Build Status](https://travis-ci.org/syrusakbary/graphene.svg?branch=master)](https://travis-ci.org/syrusakbary/graphene)
[![Coverage Status](https://coveralls.io/repos/syrusakbary/graphene/badge.svg?branch=master&service=github)](https://coveralls.io/github/syrusakbary/graphene?branch=master)

## Usage

Example code of a GraphQL schema using Graphene:

### Schema definition

```python
import graphene
# ...

class Character(graphene.Interface):
    id = graphene.IDField()
    name = graphene.StringField()
    friends = graphene.ListField('self')
    appearsIn = graphene.ListField(Episode)

    def resolve_friends(self, args, *_):
        return [wrap_character(getCharacter(f)) for f in self.instance.friends]

class Human(Character):
    homePlanet = graphene.StringField()


class Droid(Character):
    primaryFunction = graphene.StringField()


class Query(graphene.ObjectType):
    hero = graphene.Field(Character,
        episode = graphene.Argument(Episode)
    )
    human = graphene.Field(Human,
        id = graphene.Argument(graphene.String)
    )
    droid = graphene.Field(Droid,
        id = graphene.Argument(graphene.String)
    )

    @resolve_only_args
    def resolve_hero(self, episode):
        return wrap_character(getHero(episode))

    @resolve_only_args
    def resolve_human(self, id):
        return wrap_character(getHuman(id))
        if human:
            return Human(human)

    @resolve_only_args
    def resolve_droid(self, id):
        return wrap_character(getDroid(id))


Schema = graphene.Schema(query=Query)
```

### Querying

Querying `graphene.Schema` is as simple as:

```python
query = '''
    query HeroNameQuery {
      hero {
        name
      }
    }
'''
result = Schema.execute(query)
```

## Contributing

After cloning this repo, ensure dependencies are installed by running:

```sh
python setup.py install
```

After developing, the full test suite can be evaluated by running:

```sh
python setup.py test # Use --pytest-args="-v -s" for verbose mode
```
