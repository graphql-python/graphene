import graphene
from graphene import resolve_only_args, relay
from graphene.contrib.django import (
    DjangoObjectType,
    DjangoNode
)
from .models import (
    Ship as ShipModel, Faction as FactionModel, Character as CharacterModel)
from .data import (
    get_faction,
    get_ship,
    get_ships,
    get_rebels,
    get_empire,
    create_ship
)

schema = graphene.Schema(name='Starwars Django Relay Schema')


class Ship(DjangoNode):
    class Meta:
        model = ShipModel

    @classmethod
    def get_node(cls, id):
        return Ship(get_ship(id))


@schema.register
class Character(DjangoObjectType):
    class Meta:
        model = CharacterModel


class Faction(DjangoNode):
    class Meta:
        model = FactionModel

    @classmethod
    def get_node(cls, id):
        return Faction(get_faction(id))


class IntroduceShip(relay.ClientIDMutation):
    class Input:
        ship_name = graphene.StringField(required=True)
        faction_id = graphene.StringField(required=True)

    ship = graphene.Field(Ship)
    faction = graphene.Field(Faction)

    @classmethod
    def mutate_and_get_payload(cls, input, info):
        ship_name = input.get('ship_name')
        faction_id = input.get('faction_id')
        ship = create_ship(ship_name, faction_id)
        faction = get_faction(faction_id)
        return IntroduceShip(ship=ship, faction=faction)


class Query(graphene.ObjectType):
    rebels = graphene.Field(Faction)
    empire = graphene.Field(Faction)
    node = relay.NodeField()
    ships = relay.ConnectionField(Ship, description='All the ships.')

    @resolve_only_args
    def resolve_ships(self):
        return [Ship(s) for s in get_ships()]

    @resolve_only_args
    def resolve_rebels(self):
        return Faction(get_rebels())

    @resolve_only_args
    def resolve_empire(self):
        return Faction(get_empire())


class Mutation(graphene.ObjectType):
    introduce_ship = graphene.Field(IntroduceShip)


schema.query = Query
schema.mutation = Mutation
