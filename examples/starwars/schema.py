import graphene
from graphene import resolve_only_args
from graphql.core.type import GraphQLEnumValue

from .data import get_character, get_droid, get_hero, get_human

Episode = graphene.Enum('Episode', dict(
    NEWHOPE=GraphQLEnumValue(4),
    EMPIRE=GraphQLEnumValue(5),
    JEDI=GraphQLEnumValue(6)
))


class Character(graphene.Interface):
    id = graphene.IDField()
    name = graphene.StringField()
    friends = graphene.ListField('Character')
    appears_in = graphene.ListField(Episode)

    def resolve_friends(self, args, *_):
        # The character friends is a list of strings
        return [get_character(f) for f in self.friends]


class Human(Character):
    home_planet = graphene.StringField()


class Droid(Character):
    primary_function = graphene.StringField()


class Query(graphene.ObjectType):
    hero = graphene.Field(Character,
                          episode=graphene.Argument(Episode)
                          )
    human = graphene.Field(Human,
                           id=graphene.Argument(graphene.String)
                           )
    droid = graphene.Field(Droid,
                           id=graphene.Argument(graphene.String)
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
