from graphene import ObjectType, Schema, Field, String
from graphene import relay

from .data import create_ship, get_empire, get_faction, get_rebels, get_ship


class Ship(ObjectType, interfaces=(relay.Node,)):
    """A ship in the Star Wars saga."""

    name = String(description="The name of the ship.")

    @classmethod
    def get_node(cls, info, id):
        return get_ship(id)


class ShipConnection(relay.Connection, node=Ship):
    pass


class Faction(ObjectType, interfaces=(relay.Node,)):
    """A faction in the Star Wars saga."""

    name = String(description="The name of the faction.")
    ships = relay.ConnectionField(
        ShipConnection, description="The ships used by the faction."
    )

    def resolve_ships(self, info, **args):
        # Transform the instance ship_ids into real instances
        return [get_ship(ship_id) for ship_id in self.ships]

    @classmethod
    def get_node(cls, info, id):
        return get_faction(id)


class IntroduceShip(relay.ClientIDMutation):
    class Input:
        ship_name = String(required=True)
        faction_id = String(required=True)

    ship = Field(Ship)
    faction = Field(Faction)

    @classmethod
    def mutate_and_get_payload(
        cls, root, info, ship_name, faction_id, client_mutation_id=None
    ):
        ship = create_ship(ship_name, faction_id)
        faction = get_faction(faction_id)
        return IntroduceShip(ship=ship, faction=faction)


class Query(ObjectType):
    rebels = Field(Faction)
    empire = Field(Faction)
    node = relay.Node.Field()

    def resolve_rebels(self, info):
        return get_rebels()

    def resolve_empire(self, info):
        return get_empire()


class Mutation(ObjectType):
    introduce_ship = IntroduceShip.Field()


schema = Schema(query=Query, mutation=Mutation)
