# Graphene: Python DSL for GraphQL

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

    def resolve_friends(self, args, *_):
        return [Human(f) for f in self.instance.friends]

class Human(Character):
    homePlanet = graphene.StringField()

class Query(graphene.ObjectType):
    human = graphene.Field(Human)

schema = graphene.Schema(query=Query)
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
result = schema.execute(query)
```

### Relay Schema

Graphene also supports Relay, check the [Starwars Relay example](tests/starwars_relay)!

```python
class Ship(relay.Node):
    '''A ship in the Star Wars saga'''
    name = graphene.StringField(description='The name of the ship.')

    @classmethod
    def get_node(cls, id):
        return Ship(getShip(id))


class Query(graphene.ObjectType):
    ships = relay.ConnectionField(Ship, description='The ships used by the faction.')
    node = relay.NodeField()

    @resolve_only_args
    def resolve_ships(self):
        return [Ship(s) for s in getShips()]

```

### Django+Relay Schema

If you want to use graphene with your Django Models check the [Starwars Django example](tests/starwars_django)!

```python
class Ship(DjangoNode):
    class Meta:
        model = YourDjangoModelHere
        # only_fields = ('id', 'name') # Only map this fields from the model

class Query(graphene.ObjectType):
    node = relay.NodeField()
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
