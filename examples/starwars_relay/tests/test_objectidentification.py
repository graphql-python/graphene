from ..data import setup
from ..schema import schema

setup()


def test_str_schema():
    assert str(schema) == '''schema {
  query: Query
  mutation: Mutation
}

type Faction implements Node {
  id: ID!
  name: String
  ships(before: String, after: String, first: Int, last: Int): ShipConnection
}

input IntroduceShipInput {
  shipName: String!
  factionId: String!
  clientMutationId: String
}

type IntroduceShipPayload {
  ship: Ship
  faction: Faction
}

type Mutation {
  introduceShip(input: IntroduceShipInput!): IntroduceShipPayload
}

interface Node {
  id: ID!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type Query {
  rebels: Faction
  empire: Faction
  node(id: ID!): Node
}

type Ship implements Node {
  id: ID!
  name: String
}

type ShipConnection {
  pageInfo: PageInfo!
  edges: [ShipEdge]
}

type ShipEdge {
  cursor: String!
  node: Ship
}
'''


def test_correctly_fetches_id_name_rebels():
    query = '''
      query RebelsQuery {
        rebels {
          id
          name
        }
      }
    '''
    expected = {
        'rebels': {
            'id': 'RmFjdGlvbjox',
            'name': 'Alliance to Restore the Republic'
        }
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_correctly_refetches_rebels():
    query = '''
      query RebelsRefetchQuery {
        node(id: "RmFjdGlvbjox") {
          id
          ... on Faction {
            name
          }
        }
      }
    '''
    expected = {
        'node': {
            'id': 'RmFjdGlvbjox',
            'name': 'Alliance to Restore the Republic'
        }
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_correctly_fetches_id_name_empire():
    query = '''
      query EmpireQuery {
        empire {
          id
          name
        }
      }
    '''
    expected = {
        'empire': {
            'id': 'RmFjdGlvbjoy',
            'name': 'Galactic Empire'
        }
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_correctly_refetches_empire():
    query = '''
      query EmpireRefetchQuery {
        node(id: "RmFjdGlvbjoy") {
          id
          ... on Faction {
            name
          }
        }
      }
    '''
    expected = {
        'node': {
            'id': 'RmFjdGlvbjoy',
            'name': 'Galactic Empire'
        }
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected


def test_correctly_refetches_xwing():
    query = '''
      query XWingRefetchQuery {
        node(id: "U2hpcDox") {
          id
          ... on Ship {
            name
          }
        }
      }
    '''
    expected = {
        'node': {
            'id': 'U2hpcDox',
            'name': 'X-Wing'
        }
    }
    result = schema.execute(query)
    assert not result.errors
    assert result.data == expected
