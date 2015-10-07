# Graphene [![Build Status](https://travis-ci.org/graphql-python/graphene.svg?branch=master)](https://travis-ci.org/graphql-python/graphene) [![Coverage Status](https://coveralls.io/repos/graphql-python/graphene/badge.svg?branch=master&service=github)](https://coveralls.io/github/graphql-python/graphene?branch=master)

Graphene is a Python library for creating GraphQL schemas/types easly.
It maps the models/fields to internal GraphQL objects without effort.
Including automatic [Django models](#djangorelay-schema) conversion.


## Installation

For instaling graphene, just run this command in your shell

```bash
pip install graphene
```


## Usage

Example code of a GraphQL schema using Graphene:

### Schema definition

```python
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

Then Querying `graphene.Schema` is as simple as:

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
    name = graphene.StringField()

    @classmethod
    def get_node(cls, id):
        return Ship(your_ship_instance)


class Query(graphene.ObjectType):
    ships = relay.ConnectionField(Ship)
    node = relay.NodeField()

```

### Django+Relay Schema

If you want to use graphene with your Django Models check the [Starwars Django example](tests/starwars_django)!

```python
class Ship(DjangoNode):
    class Meta:
        model = YourDjangoModelHere
        # only_fields = ('id', 'name') # Only map this fields from the model
        # exclude_fields ('field_to_exclude', ) # Exclude mapping this fields from the model

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
