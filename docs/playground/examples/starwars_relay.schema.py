import graphene
from graphene import relay, resolve_only_args

class Ship(relay.Node):
    '''A ship in the Star Wars saga'''
    name = graphene.String(description='The name of the ship.')

    @classmethod
    def get_node(cls, id, info):
        return get_ship(id)

class Faction(relay.Node):
    '''A faction in the Star Wars saga'''
    name = graphene.String(description='The name of the faction.')
    ships = relay.ConnectionField(
        Ship, description='The ships used by the faction.')

    @resolve_only_args
    def resolve_ships(self, **args):
        # Transform the instance ship_ids into real instances
        return [get_ship(ship_id) for ship_id in self.ships]

    @classmethod
    def get_node(cls, id, info):
        return get_faction(id)

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
        return IntroduceShip(ship=ship, faction=faction)


class Query(graphene.ObjectType):
    rebels = graphene.Field(Faction)
    empire = graphene.Field(Faction)
    node = relay.NodeField()

    @resolve_only_args
    def resolve_rebels(self):
        return get_rebels()

    @resolve_only_args
    def resolve_empire(self):
        return get_empire()


class Mutation(graphene.ObjectType):
    introduce_ship = graphene.Field(IntroduceShip)

schema = graphene.Schema(name='Starwars Relay Schema')
schema.query = Query
schema.mutation = Mutation

xwing = Ship(
    id='1',
    name='X-Wing',
)
ywing = Ship(
    id='2',
    name='Y-Wing',
)
awing = Ship(
    id='3',
    name='A-Wing',
)

# Yeah, technically it's Corellian. But it flew in the service of the rebels,
# so for the purposes of this demo it's a rebel ship.
falcon = Ship(
    id='4',
    name='Millenium Falcon',
)
homeOne = Ship(
    id='5',
    name='Home One',
)
tieFighter = Ship(
    id='6',
    name='TIE Fighter',
)
tieInterceptor = Ship(
    id='7',
    name='TIE Interceptor',
)
executor = Ship(
    id='8',
    name='Executor',
)
rebels = Faction(
    id='1',
    name='Alliance to Restore the Republic',
    ships=['1', '2', '3', '4', '5']
)
empire = Faction(
    id='2',
    name='Galactic Empire',
    ships=['6', '7', '8']
)
data = {
    'Faction': {
        '1': rebels,
        '2': empire
    },
    'Ship': {
        '1': xwing,
        '2': ywing,
        '3': awing,
        '4': falcon,
        '5': homeOne,
        '6': tieFighter,
        '7': tieInterceptor,
        '8': executor
    }
}

def create_ship(ship_name, faction_id):
    from .schema import Ship
    next_ship = len(data['Ship'].keys()) + 1
    new_ship = Ship(
        id=str(next_ship),
        name=ship_name
    )
    data['Ship'][new_ship.id] = new_ship
    data['Faction'][faction_id].ships.append(new_ship.id)
    return new_ship

def get_ship(_id):
    return data['Ship'][_id]

def get_faction(_id):
    return data['Faction'][_id]

def get_rebels():
    return get_faction('1')

def get_empire():
    return get_faction('2')
