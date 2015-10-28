import graphene
from graphene import resolve_only_args, relay
from graphene.contrib.django import (
    DjangoObjectType,
    DjangoNode
)
from .models import (
    Ship as ShipModel, Faction as FactionModel, Character as CharacterModel)
from .data import (
    getFaction,
    getShip,
    getShips,
    getRebels,
    getEmpire,
)

schema = graphene.Schema(name='Starwars Django Relay Schema')


class Ship(DjangoNode):
    class Meta:
        model = ShipModel

    @classmethod
    def get_node(cls, id):
        return Ship(getShip(id))


@schema.register
class Character(DjangoObjectType):
    class Meta:
        model = CharacterModel


class Faction(DjangoNode):
    class Meta:
        model = FactionModel

    @classmethod
    def get_node(cls, id):
        return Faction(getFaction(id))


class Query(graphene.ObjectType):
    rebels = graphene.Field(Faction)
    empire = graphene.Field(Faction)
    node = relay.NodeField()
    ships = relay.ConnectionField(Ship, description='All the ships.')

    @resolve_only_args
    def resolve_ships(self):
        return [Ship(s) for s in getShips()]

    @resolve_only_args
    def resolve_rebels(self):
        return Faction(getRebels())

    @resolve_only_args
    def resolve_empire(self):
        return Faction(getEmpire())


schema.query = Query
