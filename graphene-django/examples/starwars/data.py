from .models import Character, Faction, Ship


def initialize():
    human = Character(
        name='Human'
    )
    human.save()

    droid = Character(
        name='Droid'
    )
    droid.save()

    rebels = Faction(
        id='1',
        name='Alliance to Restore the Republic',
        hero=human
    )
    rebels.save()

    empire = Faction(
        id='2',
        name='Galactic Empire',
        hero=droid
    )
    empire.save()

    xwing = Ship(
        id='1',
        name='X-Wing',
        faction=rebels,
    )
    xwing.save()

    ywing = Ship(
        id='2',
        name='Y-Wing',
        faction=rebels,
    )
    ywing.save()

    awing = Ship(
        id='3',
        name='A-Wing',
        faction=rebels,
    )
    awing.save()

    # Yeah, technically it's Corellian. But it flew in the service of the rebels,
    # so for the purposes of this demo it's a rebel ship.
    falcon = Ship(
        id='4',
        name='Millenium Falcon',
        faction=rebels,
    )
    falcon.save()

    homeOne = Ship(
        id='5',
        name='Home One',
        faction=rebels,
    )
    homeOne.save()

    tieFighter = Ship(
        id='6',
        name='TIE Fighter',
        faction=empire,
    )
    tieFighter.save()

    tieInterceptor = Ship(
        id='7',
        name='TIE Interceptor',
        faction=empire,
    )
    tieInterceptor.save()

    executor = Ship(
        id='8',
        name='Executor',
        faction=empire,
    )
    executor.save()


def create_ship(ship_name, faction_id):
    new_ship = Ship(
        name=ship_name,
        faction_id=faction_id
    )
    new_ship.save()
    return new_ship


def get_ship(_id):
    return Ship.objects.get(id=_id)


def get_ships():
    return Ship.objects.all()


def get_faction(_id):
    return Faction.objects.get(id=_id)


def get_rebels():
    return get_faction(1)


def get_empire():
    return get_faction(2)
