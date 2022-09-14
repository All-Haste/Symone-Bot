import pytest
from bson import DBRef
from testcontainers.mongodb import MongoDbContainer

from symone_bot.aspects import Aspect
from symone_bot.commands import Command
from symone_bot.data import DatabaseClient
from symone_bot.metadata import QueryMetaData


@pytest.fixture
def test_metadata():
    return QueryMetaData("ABCD1234")


@pytest.fixture
def test_commands():
    return {"foo": Command("foo", "does foo stuff", lambda: 1 + 1, is_modifier=True)}


@pytest.fixture
def test_aspects():
    return {"bar": Aspect("bar", "a bar aspect", "bar", value_type=int)}


@pytest.fixture(scope="module")
def mongodb():
    with MongoDbContainer("mongo:6.0.1") as mongo:
        db = mongo.get_connection_client().symone_knowledge
        result = db.game_context.insert_one(
            {
                "kind": "campaign",
                "name": "Against the Aeon Throne",
                "game_master": "U72P1S26N",
                "currency": {"quantity": 1000, "type": "credits"},
                "party": {
                    "name": "",
                    "size": 5,
                    "level": 1,
                    "xp": 0,
                    "xp_for_level_up": 500,
                    "members": {},
                },
                "loot": {},
                "system": {"name": "Starfinder", "version": 1},
            },
        )
        db.current_game_context.insert_one(
            {
                "tracking_context": True,
                "active_context": DBRef(
                    "game_context", result.inserted_id, "symone_knowledge"
                ),
            }
        )
        db.game_context.insert_one(
            {
                "kind": "campaign",
                "name": "Rise of Tiamat",
                "game_master": "U72P1S26N",
                "currency": {"quantity": 999, "type": "gold"},
                "party": {
                    "name": "The Dragon Getters",
                    "size": 3,
                    "level": 1,
                    "xp": 0,
                    "xp_for_level_up": 500,
                    "members": {},
                },
                "loot": {},
                "system": {"name": "Dungeons & Dragons", "version": 5},
            },
        )
        yield db


@pytest.fixture
def database_client(mongodb):
    return DatabaseClient(
        "test",
        mongo_user="test",
        mongo_host=f"{mongodb.client.address[0]}:{mongodb.client.address[1]}",
        mongo_scheme="mongodb",
    )
