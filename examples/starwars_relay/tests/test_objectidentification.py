from graphene.test import Client
from ..data import setup
from ..schema import schema

setup()

client = Client(schema)


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
  clientMutationId: String
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
  edges: [ShipEdge]!
}

type ShipEdge {
  node: Ship
  cursor: String!
}
'''


def test_correctly_fetches_id_name_rebels(snapshot):
    query = '''
      query RebelsQuery {
        rebels {
          id
          name
        }
      }
    '''
    snapshot.assert_match(client.execute(query))


def test_correctly_refetches_rebels(snapshot):
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
    snapshot.assert_match(client.execute(query))


def test_correctly_fetches_id_name_empire(snapshot):
    query = '''
      query EmpireQuery {
        empire {
          id
          name
        }
      }
    '''
    snapshot.assert_match(client.execute(query))


def test_correctly_refetches_empire(snapshot):
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
    snapshot.assert_match(client.execute(query))


def test_correctly_refetches_xwing(snapshot):
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
    snapshot.assert_match(client.execute(query))
