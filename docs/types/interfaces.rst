Interfaces
==========

An *Interface* is an abstract type that defines a certain set of fields that a
type must include to implement the interface.

For example, you can define an Interface ``Character`` that represents any
character in the Star Wars trilogy:

.. code:: python

    import graphene

    class Character(graphene.Interface):
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        friends = graphene.List(lambda: Character)
        appears_in = graphene.List(Episode, required=True)


Any ObjectType that implements ``Character`` will have these exact fields, with
these arguments and return types.

For example, here are some types that might implement ``Character``:

.. code:: python

    class Human(graphene.ObjectType):
        class Meta:
            interfaces = (Character, )

        starships = graphene.List(Starship)
        home_planet = graphene.String()

    class Droid(graphene.ObjectType):
        class Meta:
            interfaces = (Character, )

        primary_function = graphene.String()


Both of these types have all of the fields from the ``Character`` interface,
but also bring in extra fields, ``home_planet``, ``starships`` and
``primary_function``, that are specific to that particular type of character.

The full GraphQL schema defition will look like this:

.. code::

    interface Character {
        id: ID!
        name: String!
        friends: [Character]
        appearsIn: [Episode]!
    }

    type Human implements Character {
        id: ID!
        name: String!
        friends: [Character]
        appearsIn: [Episode]!
        starships: [Starship]
        homePlanet: String
    }

    type Droid implements Character {
        id: ID!
        name: String!
        friends: [Character]
        appearsIn: [Episode]!
        primaryFunction: String
    }

Interfaces are useful when you want to return an object or set of objects,
which might be of several different types.

For example, you can define a field ``hero`` that resolves to any
``Character``, depending on the episode, like this:

.. code:: python

    class Query(graphene.ObjectType):
        hero = graphene.Field(
            Character,
            required=True,
            episode=graphene.Int(required=True)
        )

        def resolve_hero(_, info, episode):
            # Luke is the hero of Episode V
            if episode == 5:
                return get_human(name='Luke Skywalker')
            return get_droid(name='R2-D2')

    schema = graphene.Schema(query=Query, types=[Human, Droid])

This allows you to directly query for fields that exist on the Character interface
as well as selecting specific fields on any type that implments the interface
using `inline fragments <https://graphql.org/learn/queries/#inline-fragments>`_.

For example, the following query:

.. code::

    query HeroForEpisode($episode: Int!) {
        hero(episode: $episode) {
            __typename
            name
            ... on Droid {
                primaryFunction
            }
            ... on Human {
                homePlanet
            }
        }
    }

Will return the following data with variables ``{ "episode": 4 }``:

.. code:: json

    {
        "data": {
            "hero": {
                "__typename": "Droid",
                "name": "R2-D2",
                "primaryFunction": "Astromech"
            }
        }
    }

And different data with the variables ``{ "episode": 5 }``:

.. code:: json

    {
        "data": {
            "hero": {
                "__typename": "Human",
                "name": "Luke Skywalker",
                "homePlanet": "Tatooine"
            }
        }
    }

Resolving data objects to types
-------------------------------

As you build out your schema in Graphene it is common for your resolvers to
return objects that represent the data backing your GraphQL types rather than
instances of the Graphene types (e.g. Django or SQLAlchemy models). However
when you start using Interfaces you might come across this error:

.. code::

    "Abstract type Character must resolve to an Object type at runtime for field Query.hero ..."

This happens because Graphene doesn't have enough information to convert the
data object into a Graphene type needed to resolve the ``Interface``. To solve
this you can define a ``resolve_type`` class method on the ``Interface`` which
maps a data object to a Graphene type:

.. code:: python

    class Character(graphene.Interface):
        id = graphene.ID(required=True)
        name = graphene.String(required=True)

        @classmethod
        def resolve_type(cls, instance, info):
            if instance.type == 'DROID':
                return Droid
            return Human
