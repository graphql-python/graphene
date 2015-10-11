import graphene
from graphene import resolve_only_args, relay

from .data import (
    getHero, getHuman, getCharacter, getDroid,
    Human as _Human, Droid as _Droid)

Episode = graphene.Enum('Episode', dict(
    NEWHOPE=4,
    EMPIRE=5,
    JEDI=6
))


def wrap_character(character):
    if isinstance(character, _Human):
        return Human(character)
    elif isinstance(character, _Droid):
        return Droid(character)


class Character(graphene.Interface):
    name = graphene.StringField()
    friends = relay.Connection('Character')
    appearsIn = graphene.ListField(Episode)

    def resolve_friends(self, args, *_):
        return [wrap_character(getCharacter(f)) for f in self.instance.friends]


class Human(relay.Node, Character):
    homePlanet = graphene.StringField()


class Droid(relay.Node, Character):
    primaryFunction = graphene.StringField()


class Query(graphene.ObjectType):
    hero = graphene.Field(Character,
                          episode=graphene.Argument(Episode))
    human = graphene.Field(Human,
                           id=graphene.Argument(graphene.String))
    droid = graphene.Field(Droid,
                           id=graphene.Argument(graphene.String))
    node = relay.NodeField()

    @resolve_only_args
    def resolve_hero(self, episode):
        return wrap_character(getHero(episode))

    @resolve_only_args
    def resolve_human(self, id):
        return wrap_character(getHuman(id))

    @resolve_only_args
    def resolve_droid(self, id):
        return wrap_character(getDroid(id))


Schema = graphene.Schema(query=Query)
