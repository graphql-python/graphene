import graphene
from graphene import resolve_only_args

from .data import get_character, get_droid, get_hero, get_human


class Episode(graphene.Enum):
    NEWHOPE = 4
    EMPIRE = 5
    JEDI = 6


class Character(graphene.Interface):
    id = graphene.ID()
    name = graphene.String()
    friends = graphene.List('Character')
    appears_in = graphene.List(Episode)

    def resolve_friends(self, args, *_):
        # The character friends is a list of strings
        return [get_character(f) for f in self.friends]


class Human(Character):
    home_planet = graphene.String()


class Droid(Character):
    primary_function = graphene.String()


class Query(graphene.ObjectType):
    hero = graphene.Field(Character,
                          episode=graphene.Argument(Episode)
                          )
    human = graphene.Field(Human,
                           id=graphene.String()
                           )
    droid = graphene.Field(Droid,
                           id=graphene.String()
                           )

    @resolve_only_args
    def resolve_hero(self, episode=None):
        return get_hero(episode)

    @resolve_only_args
    def resolve_human(self, id):
        return get_human(id)

    @resolve_only_args
    def resolve_droid(self, id):
        return get_droid(id)


Schema = graphene.Schema(query=Query)
