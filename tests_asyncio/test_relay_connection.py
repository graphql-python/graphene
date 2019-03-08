import pytest

from collections import OrderedDict
from graphql.execution.executors.asyncio import AsyncioExecutor

from graphql_relay.utils import base64

from graphene.types import ObjectType, Schema, String
from graphene.relay.connection import Connection, ConnectionField, PageInfo
from graphene.relay.node import Node

letter_chars = ["A", "B", "C", "D", "E"]


class Letter(ObjectType):
    class Meta:
        interfaces = (Node,)

    letter = String()


class LetterConnection(Connection):
    class Meta:
        node = Letter


class Query(ObjectType):
    letters = ConnectionField(LetterConnection)
    connection_letters = ConnectionField(LetterConnection)
    promise_letters = ConnectionField(LetterConnection)

    node = Node.Field()

    def resolve_letters(self, info, **args):
        return list(letters.values())

    async def resolve_promise_letters(self, info, **args):
        return list(letters.values())

    def resolve_connection_letters(self, info, **args):
        return LetterConnection(
            page_info=PageInfo(has_next_page=True, has_previous_page=False),
            edges=[
                LetterConnection.Edge(node=Letter(id=0, letter="A"), cursor="a-cursor")
            ],
        )


schema = Schema(Query)

letters = OrderedDict()
for i, letter in enumerate(letter_chars):
    letters[letter] = Letter(id=i, letter=letter)


def edges(selected_letters):
    return [
        {
            "node": {"id": base64("Letter:%s" % l.id), "letter": l.letter},
            "cursor": base64("arrayconnection:%s" % l.id),
        }
        for l in [letters[i] for i in selected_letters]
    ]


def cursor_for(ltr):
    letter = letters[ltr]
    return base64("arrayconnection:%s" % letter.id)


def execute(args=""):
    if args:
        args = "(" + args + ")"

    return schema.execute(
        """
    {
        letters%s {
            edges {
                node {
                    id
                    letter
                }
                cursor
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
                startCursor
                endCursor
            }
        }
    }
    """
        % args
    )


@pytest.mark.asyncio
async def test_connection_promise():
    result = await schema.execute(
        """
    {
        promiseLetters(first:1) {
            edges {
                node {
                    id
                    letter
                }
            }
            pageInfo {
                hasPreviousPage
                hasNextPage
            }
        }
    }
    """,
        executor=AsyncioExecutor(),
        return_promise=True,
    )

    assert not result.errors
    assert result.data == {
        "promiseLetters": {
            "edges": [{"node": {"id": "TGV0dGVyOjA=", "letter": "A"}}],
            "pageInfo": {"hasPreviousPage": False, "hasNextPage": True},
        }
    }
