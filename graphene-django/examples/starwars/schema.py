import graphene
from graphene import relay, resolve_only_args, Schema
from graphene_django import DjangoObjectType

from .data import (create_ship, get_empire, get_faction, get_rebels, get_ship,
                   get_ships)
from .models import (
    Character as CharacterModel,
    Faction as FactionModel,
    Ship as ShipModel
)


class Ship(DjangoObjectType):

    class Meta:
        model = ShipModel
        interfaces = (relay.Node, )

    @classmethod
    def get_node(cls, id, context, info):
        node = get_ship(id)
        print(node)
        return node


class Character(DjangoObjectType):

    class Meta:
        model = CharacterModel


class Faction(DjangoObjectType):

    class Meta:
        model = FactionModel
        interfaces = (relay.Node, )

    @classmethod
    def get_node(cls, id, context, info):
        return get_faction(id)


class IntroduceShip(relay.ClientIDMutation):

    class Input:
        ship_name = graphene.String(required=True)
        faction_id = graphene.String(required=True)

    ship = graphene.Field(Ship)
    faction = graphene.Field(Faction)

    @classmethod
    def mutate_and_get_payload(cls, input, context, info):
        ship_name = input.get('shipName')
        faction_id = input.get('factionId')
        ship = create_ship(ship_name, faction_id)
        faction = get_faction(faction_id)
        return IntroduceShip(ship=ship, faction=faction)


class Query(graphene.ObjectType):
    rebels = graphene.Field(Faction)
    empire = graphene.Field(Faction)
    node = relay.Node.Field()
    ships = relay.ConnectionField(Ship, description='All the ships.')

    @resolve_only_args
    def resolve_ships(self):
        return get_ships()

    @resolve_only_args
    def resolve_rebels(self):
        return get_rebels()

    @resolve_only_args
    def resolve_empire(self):
        return get_empire()


class Mutation(graphene.ObjectType):
    introduce_ship = IntroduceShip.Field()


# We register the Character Model because if not would be
# inaccessible for the schema
schema = Schema(query=Query, mutation=Mutation, types=[Ship, Character])
