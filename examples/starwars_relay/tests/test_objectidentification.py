import textwrap

from graphene.test import Client

from ..data import setup
from ..schema import schema

setup()

client = Client(schema)


def test_str_schema():
    assert str(schema).strip() == textwrap.dedent(
        '''\
        type Query {
          rebels: Faction
          empire: Faction
          node(
            """The ID of the object"""
            id: ID!
          ): Node
        }

        """A faction in the Star Wars saga"""
        type Faction implements Node {
          """The ID of the object"""
          id: ID!

          """The name of the faction."""
          name: String

          """The ships used by the faction."""
          ships(before: String, after: String, first: Int, last: Int): ShipConnection
        }

        """An object with an ID"""
        interface Node {
          """The ID of the object"""
          id: ID!
        }

        type ShipConnection {
          """Pagination data for this connection."""
          pageInfo: PageInfo!

          """Contains the nodes in this connection."""
          edges: [ShipEdge]!
        }

        """
        The Relay compliant `PageInfo` type, containing data necessary to paginate this connection.
        """
        type PageInfo {
          """When paginating forwards, are there more items?"""
          hasNextPage: Boolean!

          """When paginating backwards, are there more items?"""
          hasPreviousPage: Boolean!

          """When paginating backwards, the cursor to continue."""
          startCursor: String

          """When paginating forwards, the cursor to continue."""
          endCursor: String
        }

        """A Relay edge containing a `Ship` and its cursor."""
        type ShipEdge {
          """The item at the end of the edge"""
          node: Ship

          """A cursor for use in pagination"""
          cursor: String!
        }

        """A ship in the Star Wars saga"""
        type Ship implements Node {
          """The ID of the object"""
          id: ID!

          """The name of the ship."""
          name: String
        }

        type Mutation {
          introduceShip(input: IntroduceShipInput!): IntroduceShipPayload
        }

        type IntroduceShipPayload {
          ship: Ship
          faction: Faction
          clientMutationId: String
        }

        input IntroduceShipInput {
          shipName: String!
          factionId: String!
          clientMutationId: String
        }'''
    )


def test_correctly_fetches_id_name_rebels():
    result = client.execute("""
      query RebelsQuery {
        rebels {
          id
          name
        }
      }
    """)
    assert result == {
        "data": {
            "rebels": {"id": "RmFjdGlvbjox", "name": "Alliance to Restore the Republic"}
        }
    }


def test_correctly_refetches_rebels():
    result = client.execute("""
      query RebelsRefetchQuery {
        node(id: "RmFjdGlvbjox") {
          id
          ... on Faction {
            name
          }
        }
      }
    """)
    assert result == {
        "data": {
            "node": {"id": "RmFjdGlvbjox", "name": "Alliance to Restore the Republic"}
        }
    }


def test_correctly_fetches_id_name_empire():
    result = client.execute("""
      query EmpireQuery {
        empire {
          id
          name
        }
      }
    """)
    assert result == {
        "data": {"empire": {"id": "RmFjdGlvbjoy", "name": "Galactic Empire"}}
    }


def test_correctly_refetches_empire():
    result = client.execute("""
      query EmpireRefetchQuery {
        node(id: "RmFjdGlvbjoy") {
          id
          ... on Faction {
            name
          }
        }
      }
    """)
    assert result == {
        "data": {"node": {"id": "RmFjdGlvbjoy", "name": "Galactic Empire"}}
    }


def test_correctly_refetches_xwing():
    result = client.execute("""
      query XWingRefetchQuery {
        node(id: "U2hpcDox") {
          id
          ... on Ship {
            name
          }
        }
      }
    """)
    assert result == {"data": {"node": {"id": "U2hpcDox", "name": "X-Wing"}}}
