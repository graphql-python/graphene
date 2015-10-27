from graphql.core.type import GraphQLEnumValue
import graphene
from graphene import resolve_only_args

from .data import getHero, getHuman, getCharacter, getDroid

Episode = graphene.Enum('Episode', dict(
    NEWHOPE=GraphQLEnumValue(4),
    EMPIRE=GraphQLEnumValue(5),
    JEDI=GraphQLEnumValue(6)
))


class Character(graphene.Interface):
    id = graphene.IDField()
    name = graphene.StringField()
    friends = graphene.ListField('self')
    appears_in = graphene.ListField(Episode)

    def resolve_friends(self, args, *_):
        # The character friends is a list of strings
        return [getCharacter(f) for f in self.friends]


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

    class Meta:
        type_name = 'core_Query'

    @resolve_only_args
    def resolve_hero(self, episode=None):
        return getHero(episode)

    @resolve_only_args
    def resolve_human(self, id):
        return getHuman(id)

    @resolve_only_args
    def resolve_droid(self, id):
        return getDroid(id)


Schema = graphene.Schema(query=Query)
