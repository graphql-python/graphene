import graphene
from graphene import relay, resolve_only_args
from graphene.contrib.django import DjangoNode, DjangoObjectType

from .data import (create_ship, get_empire, get_faction, get_rebels, get_ship,
                   get_ships)
from .models import Character as CharacterModel
from .models import Faction as FactionModel
from .models import Ship as ShipModel

schema = graphene.Schema(name='Starwars Django Relay Schema')


class Ship(DjangoNode):

    class Meta:
        model = ShipModel

    @classmethod
    def get_node(cls, id, info):
        return Ship(get_ship(id))


class Character(DjangoObjectType):

    class Meta:
        model = CharacterModel


class Faction(DjangoNode):

    class Meta:
        model = FactionModel

    @classmethod
    def get_node(cls, id, info):
        return Faction(get_faction(id))


class IntroduceShip(relay.ClientIDMutation):

    class Input:
        ship_name = graphene.String(required=True)
        faction_id = graphene.String(required=True)

    ship = graphene.Field(Ship)
    faction = graphene.Field(Faction)

    @classmethod
    def mutate_and_get_payload(cls, input, info):
        ship_name = input.get('ship_name')
        faction_id = input.get('faction_id')
        ship = create_ship(ship_name, faction_id)
        faction = get_faction(faction_id)
        return IntroduceShip(ship=Ship(ship), faction=Faction(faction))


class Query(graphene.ObjectType):
    rebels = graphene.Field(Faction)
    empire = graphene.Field(Faction)
    node = relay.NodeField()
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
    introduce_ship = graphene.Field(IntroduceShip)


# We register the Character Model because if not would be
# inaccessible for the schema
schema.register(Character)

schema.query = Query
schema.mutation = Mutation
