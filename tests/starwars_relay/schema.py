import graphene
from graphene import resolve_only_args, relay

from .data import (
    getFaction,
    getShip,
    getRebels,
    getEmpire,
)

schema = graphene.Schema(name='Starwars Relay Schema')

class Ship(relay.Node):
    '''A ship in the Star Wars saga'''
    name = graphene.StringField(description='The name of the ship.')

    @classmethod
    def get_node(cls, id):
        return Ship(getShip(id))


class Faction(relay.Node):
    '''A faction in the Star Wars saga'''
    name = graphene.StringField(description='The name of the faction.')
    ships = relay.ConnectionField(Ship, description='The ships used by the faction.')

    @resolve_only_args
    def resolve_ships(self, **kwargs):
        return [Ship(getShip(ship)) for ship in self.instance.ships]

    @classmethod
    def get_node(cls, id):
        return Faction(getFaction(id))


class Query(graphene.ObjectType):
    rebels = graphene.Field(Faction)
    empire = graphene.Field(Faction)
    node = relay.NodeField()

    @resolve_only_args
    def resolve_rebels(self):
        return Faction(getRebels())

    @resolve_only_args
    def resolve_empire(self):
        return Faction(getEmpire())


schema.query = Query
