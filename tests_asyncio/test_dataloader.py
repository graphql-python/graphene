from collections import namedtuple
from unittest.mock import Mock
from pytest import mark
from aiodataloader import DataLoader

from graphene import ObjectType, String, Schema, Field, List


CHARACTERS = {
    "1": {"name": "Luke Skywalker", "sibling": "3"},
    "2": {"name": "Darth Vader", "sibling": None},
    "3": {"name": "Leia Organa", "sibling": "1"},
}


get_character = Mock(side_effect=lambda character_id: CHARACTERS[character_id])


class CharacterType(ObjectType):
    name = String()
    sibling = Field(lambda: CharacterType)

    async def resolve_sibling(character, info):
        if character["sibling"]:
            return await info.context.character_loader.load(character["sibling"])
        return None


class Query(ObjectType):
    skywalker_family = List(CharacterType)

    async def resolve_skywalker_family(_, info):
        return await info.context.character_loader.load_many(["1", "2", "3"])


mock_batch_load_fn = Mock(
    side_effect=lambda character_ids: [get_character(id) for id in character_ids]
)


class CharacterLoader(DataLoader):
    async def batch_load_fn(self, character_ids):
        return mock_batch_load_fn(character_ids)


Context = namedtuple("Context", "character_loader")


@mark.asyncio
async def test_basic_dataloader():
    schema = Schema(query=Query)

    character_loader = CharacterLoader()
    context = Context(character_loader=character_loader)

    query = """
        {
            skywalkerFamily {
                name
                sibling {
                    name
                }
            }
        }
    """

    result = await schema.execute_async(query, context=context)

    assert not result.errors
    assert result.data == {
        "skywalkerFamily": [
            {"name": "Luke Skywalker", "sibling": {"name": "Leia Organa"}},
            {"name": "Darth Vader", "sibling": None},
            {"name": "Leia Organa", "sibling": {"name": "Luke Skywalker"}},
        ]
    }

    assert mock_batch_load_fn.call_count == 1
    assert get_character.call_count == 3
