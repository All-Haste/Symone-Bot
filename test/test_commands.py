import pytest

from symone_bot.aspects import aspect_dict
from symone_bot.commands import (
    Command,
    add,
    default_response,
    help_message,
)


def test_command_raises_attribute_error_when_function_not_callable():
    with pytest.raises(AttributeError):
        Command("foo", "bar", "strings aren't callable")


def test_command_help():
    command = Command("foo", "bar", lambda: 1 + 1)
    actual = command.help()
    assert actual == "`foo`: bar."


def test_default_response(test_metadata):
    actual = default_response(test_metadata)
    assert actual["response_type"] == "ephemeral"
    assert actual["text"] == "I'm sorry, I don't understand."


def test_help_message(test_metadata, test_commands):
    actual = help_message(test_metadata)

    assert actual["response_type"] == "ephemeral"
    assert "`help`: retrieves help info.\n" in actual["text"]


def test_add_deny_unallowed_user(test_metadata, test_aspects, database_client):
    aspect = test_aspects.get("bar")
    actual = add(metadata=test_metadata, aspect=aspect, value=100)

    assert actual["response_type"] == "in_channel"
    assert actual["text"] == "Nice try..."


def test_add(test_metadata, test_aspects, database_client):
    test_metadata.user_id = database_client.get_game_master()
    aspect = aspect_dict.get("xp")
    actual = add(metadata=test_metadata, aspect=aspect, value=100)

    assert actual["response_type"] == "in_channel"
    assert actual["text"] == "Updated xp to 100"
