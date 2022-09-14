import pytest


def test_get_current_campaign_id(database_client):
    current_campaign_id = database_client.get_context_tracker()

    assert current_campaign_id is not None


def test_get_current_game_context_raises_when_no_context(database_client):
    database_client.db.current_game_context.delete_many({})
    with pytest.raises(Exception):
        database_client.get_current_game_context()


def test_get_context_by_campaign_name_raises_when_multiple_matches(database_client):
    database_client.db.game_context.insert_many(
        [
            {"name": "Against the Aeon Throne"},
            {"name": "Against the Aeon Throne"},
        ]
    )
    with pytest.raises(Exception):
        database_client.get_context_by_campaign_name("Against the Aeon Throne")


def test_get_context_tracker_raises_when_no_context(database_client):
    database_client.db.current_game_context.delete_many({})
    with pytest.raises(Exception):
        database_client.get_context_tracker()
