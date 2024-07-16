from graphene.test import Client

from ..data import setup
from ..schema import schema

setup()

client = Client(schema)


def test_hero_name_query():
    result = client.execute("""
        query HeroNameQuery {
          hero {
            name
          }
        }
    """)
    assert result == {"data": {"hero": {"name": "R2-D2"}}}


def test_hero_name_and_friends_query():
    result = client.execute("""
        query HeroNameAndFriendsQuery {
          hero {
            id
            name
            friends {
              name
            }
          }
        }
    """)
    assert result == {
        "data": {
            "hero": {
                "id": "2001",
                "name": "R2-D2",
                "friends": [
                    {"name": "Luke Skywalker"},
                    {"name": "Han Solo"},
                    {"name": "Leia Organa"},
                ],
            }
        }
    }


def test_nested_query():
    result = client.execute("""
        query NestedQuery {
          hero {
            name
            friends {
              name
              appearsIn
              friends {
                name
              }
            }
          }
        }
    """)
    assert result == {
        "data": {
            "hero": {
                "name": "R2-D2",
                "friends": [
                    {
                        "name": "Luke Skywalker",
                        "appearsIn": ["NEWHOPE", "EMPIRE", "JEDI"],
                        "friends": [
                            {"name": "Han Solo"},
                            {"name": "Leia Organa"},
                            {"name": "C-3PO"},
                            {"name": "R2-D2"},
                        ],
                    },
                    {
                        "name": "Han Solo",
                        "appearsIn": ["NEWHOPE", "EMPIRE", "JEDI"],
                        "friends": [
                            {"name": "Luke Skywalker"},
                            {"name": "Leia Organa"},
                            {"name": "R2-D2"},
                        ],
                    },
                    {
                        "name": "Leia Organa",
                        "appearsIn": ["NEWHOPE", "EMPIRE", "JEDI"],
                        "friends": [
                            {"name": "Luke Skywalker"},
                            {"name": "Han Solo"},
                            {"name": "C-3PO"},
                            {"name": "R2-D2"},
                        ],
                    },
                ],
            }
        }
    }


def test_fetch_luke_query():
    result = client.execute("""
        query FetchLukeQuery {
          human(id: "1000") {
            name
          }
        }
    """)
    assert result == {"data": {"human": {"name": "Luke Skywalker"}}}


def test_fetch_some_id_query():
    result = client.execute(
        """
        query FetchSomeIDQuery($someId: String!) {
          human(id: $someId) {
            name
          }
        }
    """,
        variables={"someId": "1000"},
    )
    assert result == {"data": {"human": {"name": "Luke Skywalker"}}}


def test_fetch_some_id_query2():
    result = client.execute(
        """
        query FetchSomeIDQuery($someId: String!) {
          human(id: $someId) {
            name
          }
        }
    """,
        variables={"someId": "1002"},
    )
    assert result == {"data": {"human": {"name": "Han Solo"}}}


def test_invalid_id_query():
    result = client.execute(
        """
        query humanQuery($id: String!) {
          human(id: $id) {
            name
          }
        }
    """,
        variables={"id": "not a valid id"},
    )
    assert result == {"data": {"human": None}}


def test_fetch_luke_aliased():
    result = client.execute("""
        query FetchLukeAliased {
          luke: human(id: "1000") {
            name
          }
        }
    """)
    assert result == {"data": {"luke": {"name": "Luke Skywalker"}}}


def test_fetch_luke_and_leia_aliased():
    result = client.execute("""
        query FetchLukeAndLeiaAliased {
          luke: human(id: "1000") {
            name
          }
          leia: human(id: "1003") {
            name
          }
        }
    """)
    assert result == {
        "data": {"luke": {"name": "Luke Skywalker"}, "leia": {"name": "Leia Organa"}}
    }


def test_duplicate_fields():
    result = client.execute("""
        query DuplicateFields {
          luke: human(id: "1000") {
            name
            homePlanet
          }
          leia: human(id: "1003") {
            name
            homePlanet
          }
        }
    """)
    assert result == {
        "data": {
            "luke": {"name": "Luke Skywalker", "homePlanet": "Tatooine"},
            "leia": {"name": "Leia Organa", "homePlanet": "Alderaan"},
        }
    }


def test_use_fragment():
    result = client.execute("""
        query UseFragment {
          luke: human(id: "1000") {
            ...HumanFragment
          }
          leia: human(id: "1003") {
            ...HumanFragment
          }
        }
        fragment HumanFragment on Human {
          name
          homePlanet
        }
    """)
    assert result == {
        "data": {
            "luke": {"name": "Luke Skywalker", "homePlanet": "Tatooine"},
            "leia": {"name": "Leia Organa", "homePlanet": "Alderaan"},
        }
    }


def test_check_type_of_r2():
    result = client.execute("""
        query CheckTypeOfR2 {
          hero {
            __typename
            name
          }
        }
    """)
    assert result == {"data": {"hero": {"__typename": "Droid", "name": "R2-D2"}}}


def test_check_type_of_luke():
    result = client.execute("""
        query CheckTypeOfLuke {
          hero(episode: EMPIRE) {
            __typename
            name
          }
        }
    """)
    assert result == {
        "data": {"hero": {"__typename": "Human", "name": "Luke Skywalker"}}
    }
