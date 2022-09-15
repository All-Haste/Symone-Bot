import pytest

from symone_bot.bot_ingress import symone_message
from symone_bot.handler_source import HandlerSource


class TestBot:
    @pytest.fixture
    def game_master(self, database_client):
        return database_client.get_game_master()

    @pytest.mark.parametrize(
        "input_text, expected_response",
        [
            (
                "add xp 100",
                "Updated xp to 100",
            ),
            (
                "add 100 to xp",
                "Updated xp to 100",
            ),
            (
                "add gold 1000",
                "Updated gold to 2000",
            ),
            (
                "add 1000 to gold",
                "Updated gold to 2000",
            ),
            (
                "add xp_target 1000",
                "Updated xp_target to 1500",
            ),
            (
                "add 1000 to xp_target",
                "Updated xp_target to 1500",
            ),
            (
                "add party_size 5",
                "Updated party_size to 10",
            ),
            (
                "add 5 to party_size",
                "Updated party_size to 10",
            ),
            ("remove xp 1000", "Reduced xp to -1000"),
            ("remove 1000 from xp", "Reduced xp to -1000"),
            ("remove gold 1000", "Reduced gold to 0"),
            ("remove 1000 from gold", "Reduced gold to 0"),
            (
                "remove xp_target 1000",
                "Reduced xp_target to -500",
            ),
            (
                "remove 1000 from xp_target",
                "Reduced xp_target to -500",
            ),
            (
                "remove party_size 5",
                "Reduced party_size to 0",
            ),
            (
                "remove 5 from party_size",
                "Reduced party_size to 0",
            ),
            (
                "current xp",
                "xp is currently 0",
            ),
            (
                "current gold",
                "gold is currently 1000",
            ),
            (
                "current xp_target",
                "xp_target is currently 500",
            ),
            (
                "current party_size",
                "party_size is currently 5",
            ),
            (
                "set xp 1000",
                "Set xp to 1000",
            ),
            (
                "set xp to 1000",
                "Set xp to 1000",
            ),
            (
                "set gold 1000",
                "Set gold to 1000",
            ),
            (
                "set gold to 1000",
                "Set gold to 1000",
            ),
            (
                "set xp_target 1000",
                "Set xp_target to 1000",
            ),
            (
                "set xp_target to 1000",
                "Set xp_target to 1000",
            ),
            (
                "set party_size 1000",
                "Set party_size to 1000",
            ),
            (
                "set party_size to 1000",
                "Set party_size to 1000",
            ),
        ],
    )
    def test_interactions(self, game_master, input_text, expected_response):
        response = symone_message(
            input_text,
            game_master,
            HandlerSource.ASPECT_QUERY,
        )

        assert response["text"] == expected_response

    @pytest.mark.parametrize(
        "input_text",
        [
            "add 30 chickens",
            "add 10 to gold",
            "add 10 to xp_target",
        ],
    )
    def test_reject_unallowed_user(self, input_text):
        response = symone_message(
            input_text,
            "foobar",
            HandlerSource.ASPECT_QUERY,
        )

        assert response["text"] == "Nice try..."

    def test_help_interaction(self):
        response = symone_message("What can you do Symone?", "1234", HandlerSource.HELP)
        assert "help" in response["text"]

    def test_interaction_with_blank_input(self):
        with pytest.raises(ValueError):
            symone_message("", "1234", HandlerSource.ASPECT_QUERY)

    def test_interaction_with_no_user_id(self):
        response = symone_message("What can you do Symone?", None, HandlerSource.HELP)
        assert (
            response["text"]
            == "Sorry, Slack told me your user ID is blank? That's weird. Please try again."
        )

    def test_add_xp_level_up_threshold(self, game_master):
        symone_message("set xp_target to 1000", game_master, HandlerSource.ASPECT_QUERY)
        symone_message("set xp to 0", game_master, HandlerSource.ASPECT_QUERY)
        response = symone_message(
            "add xp 1000", game_master, HandlerSource.ASPECT_QUERY
        )

        assert (
            response["text"]
            == "Updated xp to 1000. The party leveled up! :tada: You're now level 2!"
        )
