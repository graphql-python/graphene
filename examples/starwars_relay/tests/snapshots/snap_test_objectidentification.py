# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_correctly_fetches_id_name_rebels 1"] = {
    "data": {
        "rebels": {"id": "RmFjdGlvbjox", "name": "Alliance to Restore the Republic"}
    }
}

snapshots["test_correctly_refetches_rebels 1"] = {
    "data": {"node": {"id": "RmFjdGlvbjox", "name": "Alliance to Restore the Republic"}}
}

snapshots["test_correctly_fetches_id_name_empire 1"] = {
    "data": {"empire": {"id": "RmFjdGlvbjoy", "name": "Galactic Empire"}}
}

snapshots["test_correctly_refetches_empire 1"] = {
    "data": {"node": {"id": "RmFjdGlvbjoy", "name": "Galactic Empire"}}
}

snapshots["test_correctly_refetches_xwing 1"] = {
    "data": {"node": {"id": "U2hpcDox", "name": "X-Wing"}}
}

snapshots[
    "test_str_schema 1"
] = '''type Query {
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
  ships(before: String = null, after: String = null, first: Int = null, last: Int = null): ShipConnection
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
}
'''
