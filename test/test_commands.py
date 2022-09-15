import pytest

from symone_bot.aspects import aspect_dict, Aspect
from symone_bot.commands import (
    Command,
    add,
    default_response,
    help_message,
    current,
    remove,
    switch_campaign,
    _compute_new_value,
    _add_and_remove_handler,
    set_aspect,
)


def test_init_sanity_check():
    command = Command(
        "foo", "bar", lambda: 1 + 1, Aspect("bar", "", ""), is_modifier=True
    )
    assert command.name == "foo"
    assert command.help_info == "bar"
    assert command.callable() == 2
    assert command.aspect_type.name == "bar"


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


def test_add(test_metadata, database_client, sample_game_context_1):
    test_metadata.user_id = database_client.get_game_master()
    aspect = aspect_dict.get("xp")
    actual = add(metadata=test_metadata, aspect=aspect, value=100)

    assert actual["response_type"] == "in_channel"
    assert actual["text"] == "Updated xp to 100"


def test_add_to_singleton_aspect_should_reject(test_metadata, database_client):
    test_metadata.user_id = database_client.get_game_master()
    aspect = aspect_dict.get("campaign")
    actual = add(metadata=test_metadata, aspect=aspect, value=100)

    assert actual["response_type"] == "in_channel"
    assert (
        actual["text"] == "campaign is a singleton aspect, you can't call `add` on it."
    )


@pytest.mark.parametrize(
    "aspect_name, expected",
    [
        ("xp", "xp is currently 0"),
        ("campaign", "campaign is currently Against the Aeon Throne"),
        ("xp_target", "xp_target is currently 500"),
        ("gold", "gold is currently 1000"),
        ("party_size", "party_size is currently 5"),
    ],
)
def test_current(test_metadata, database_client, aspect_name, expected):
    aspect = aspect_dict.get(aspect_name)
    actual = current(metadata=test_metadata, aspect=aspect)

    assert actual["response_type"] == "in_channel"
    assert actual["text"] == expected


def test_remove(test_metadata, database_client):
    current_xp = database_client.get_current_game_context()["party"]["xp"]
    test_metadata.user_id = database_client.get_game_master()
    aspect = aspect_dict.get("xp")
    actual = remove(metadata=test_metadata, aspect=aspect, value=100)

    assert actual["response_type"] == "in_channel"
    assert actual["text"] == f"Reduced xp to {current_xp - 100}"


def test_remove_deny_unallowed_user(test_metadata, test_aspects, database_client):
    aspect = test_aspects.get("bar")
    actual = remove(metadata=test_metadata, aspect=aspect, value=100)

    assert actual["response_type"] == "in_channel"
    assert actual["text"] == "Nice try..."


def test_remove_from_singleton_aspect_should_reject(test_metadata, database_client):
    test_metadata.user_id = database_client.get_game_master()
    aspect = aspect_dict.get("campaign")
    actual = remove(metadata=test_metadata, aspect=aspect, value=100)

    assert actual["response_type"] == "in_channel"
    assert (
        actual["text"]
        == "campaign is a singleton aspect, you can't call `remove` on it."
    )


def test_set_deny_unallowed_user(test_metadata, test_aspects, database_client):
    aspect = test_aspects.get("bar")
    actual = set_aspect(metadata=test_metadata, aspect=aspect, value=100)

    assert actual["response_type"] == "in_channel"
    assert actual["text"] == "Nice try..."


def test_switch_campaign(test_metadata, database_client):
    actual = switch_campaign(metadata=test_metadata, value="Rise of Tiamat")

    assert actual["response_type"] == "in_channel"
    assert actual["text"] == "Current campaign set to Rise of Tiamat"
    assert database_client.get_current_game_context()["name"] == "Rise of Tiamat"


def test_switch_campaign_to_non_existant_campaign(test_metadata, database_client):
    actual = switch_campaign(metadata=test_metadata, value="Not a real campaign")

    assert actual["response_type"] == "in_channel"
    assert (
        actual["text"]
        == "Error finding campaign: `Not a real campaign`, make sure case is correct."
    )


def test_compute_new_value_raises_with_wrong_sign():
    with pytest.raises(ValueError):
        _compute_new_value(100, 100, "/")


def test_compute_new_value_with_add():
    actual = _compute_new_value(100, 100, "+")
    assert actual == 200


def test_compute_new_value_with_subtract():
    actual = _compute_new_value(100, 100, "-")
    assert actual == 0


def test_add_and_remove_handler_raises_with_wrong_operator():
    with pytest.raises(ValueError):
        _add_and_remove_handler(Aspect("bar", "", ""), 100, "foo")
