import pytest

from symone_bot.bot_ingress import symone_message
from symone_bot.handler_source import HandlerSource


class TestBot:
    @pytest.fixture
    def game_master(self, database_client):
        return database_client.get_game_master()

    @pytest.mark.parametrize(
        "input_text, expected_response, handler_source",
        [
            ("add xp 1000", "Updated xp to 1000", HandlerSource.ASPECT_QUERY),
            ("add 1000 to xp", "Updated xp to 1000", HandlerSource.ASPECT_QUERY),
            ("add gold 1000", "Updated gold to 2000", HandlerSource.ASPECT_QUERY),
            ("add 1000 to gold", "Updated gold to 2000", HandlerSource.ASPECT_QUERY),
            (
                "add xp_target 1000",
                "Updated xp_target to 1500",
                HandlerSource.ASPECT_QUERY,
            ),
            (
                "add 1000 to xp_target",
                "Updated xp_target to 1500",
                HandlerSource.ASPECT_QUERY,
            ),
            (
                "add party_size 5",
                "Updated party_size to 10",
                HandlerSource.ASPECT_QUERY,
            ),
            (
                "add 5 to party_size",
                "Updated party_size to 10",
                HandlerSource.ASPECT_QUERY,
            ),
            ("remove xp 1000", "Reduced xp to -1000", HandlerSource.ASPECT_QUERY),
            ("remove 1000 from xp", "Reduced xp to -1000", HandlerSource.ASPECT_QUERY),
            ("remove gold 1000", "Reduced gold to 0", HandlerSource.ASPECT_QUERY),
            ("remove 1000 from gold", "Reduced gold to 0", HandlerSource.ASPECT_QUERY),
            (
                "remove xp_target 1000",
                "Reduced xp_target to -500",
                HandlerSource.ASPECT_QUERY,
            ),
            (
                "remove 1000 from xp_target",
                "Reduced xp_target to -500",
                HandlerSource.ASPECT_QUERY,
            ),
            (
                "remove party_size 5",
                "Reduced party_size to 0",
                HandlerSource.ASPECT_QUERY,
            ),
            (
                "remove 5 from party_size",
                "Reduced party_size to 0",
                HandlerSource.ASPECT_QUERY,
            ),
            ("current xp", "xp is currently 0", HandlerSource.ASPECT_QUERY),
            ("current gold", "gold is currently 1000", HandlerSource.ASPECT_QUERY),
            (
                "current xp_target",
                "xp_target is currently 500",
                HandlerSource.ASPECT_QUERY,
            ),
            (
                "current party_size",
                "party_size is currently 5",
                HandlerSource.ASPECT_QUERY,
            ),
        ],
    )
    def test_interactions(
        self, game_master, input_text, expected_response, handler_source
    ):
        response = symone_message(input_text, game_master, handler_source)

        assert response["text"] == expected_response

    def test_help_interaction(self):
        response = symone_message("What can you do Symone?", "1234", HandlerSource.HELP)
        assert "help" in response["text"]

    def test_interaction_with_blank_input(self):
        with pytest.raises(ValueError):
            symone_message("", "1234", HandlerSource.ASPECT_QUERY)
