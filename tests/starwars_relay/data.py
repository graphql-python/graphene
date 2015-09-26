from collections import namedtuple

Ship = namedtuple('Ship',['id', 'name'])
Faction = namedtuple('Faction',['id', 'name', 'ships'])

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
    ships= ['6', '7', '8']
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

def createShip(shipName, factionId):
    nextShip = len(data['Ship'].keys())+1
    newShip = Ship(
        id=str(nextShip),
        name=shipName
    )
    data['Ship'][newShip.id] = newShip
    data['Faction'][factionId].ships.append(newShip.id)
    return newShip


def getShip(_id):
    return data['Ship'][_id]

def getFaction(_id):
    return data['Faction'][_id]

def getRebels():
    return rebels

def getEmpire():
    return empire
