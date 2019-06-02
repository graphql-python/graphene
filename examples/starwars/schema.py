from graphene import Enum, Interface, ID, List, ObjectType, String, Field, Schema

from .data import get_character, get_droid, get_hero, get_human


class Episode(Enum):
    NEWHOPE = 4
    EMPIRE = 5
    JEDI = 6


class Character(Interface):
    id = ID()
    name = String()
    friends = List(lambda: Character)
    appears_in = List(Episode)

    def resolve_friends(self, info):
        # The character friends is a list of strings
        return [get_character(f) for f in self.friends]


class Human(ObjectType, interfaces=(Character,)):
    home_planet = String()


class Droid(ObjectType, interfaces=(Character,)):
    primary_function = String()


class Query(ObjectType):
    hero = Field(Character, episode=Episode())
    human = Field(Human, id=String())
    droid = Field(Droid, id=String())

    def resolve_hero(self, info, episode=None):
        return get_hero(episode)

    def resolve_human(self, info, id):
        return get_human(id)

    def resolve_droid(self, info, id):
        return get_droid(id)


schema = Schema(query=Query)
