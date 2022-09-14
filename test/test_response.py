import pytest
from flask import Response

from symone_bot.aspects import Aspect, aspect_dict
from symone_bot.commands import Command, command_dict, current
from symone_bot.metadata import QueryMetaData
from symone_bot.prepositions import Preposition, PrepositionType
from symone_bot.response import SymoneResponse


def test_init_sanity_check():
    command = Command("foo", "", lambda: 1 + 1)
    command.is_modifier = True
    response = SymoneResponse(
        command,
        metadata=QueryMetaData("foo"),
        aspect=Aspect("bar", "", "", value_type=str),
        value="test",
        preposition=Preposition("to", PrepositionType.DIRECTIONAL),
    )

    assert response.command.name == "foo"
    assert response.metadata.user_id == "foo"
    assert response.aspect.name == "bar"
    assert response.value == "test"
    assert response.preposition.name == "to"


def test_init_does_not_reject_default():
    try:
        command = Command("default", "", current)
        command.is_modifier = False
        SymoneResponse(
            command,
            aspect=Aspect("bar", "", "", value_type=str),
            value="foo",
        )
    except AttributeError:
        assert False, "Should not have raised AttributeError"


def test_init_does_not_check_attributes_of_singleton_aspects():
    try:
        command = Command("default", "", current, is_modifier=True)
        aspect = Aspect("bar", "", "", value_type=str, is_singleton=True)
        SymoneResponse(command, aspect=aspect, value=1)
    except AttributeError:
        assert (
            False
        ), "Should not have raised AttributeError, singleton aspects do not have value types to check"


def test_check_modifier_command_attributes_raises_when_value_type_is_none_and_value_is_not():
    with pytest.raises(AttributeError):
        aspect = Aspect("bar", "", "", value_type=None)
        value = "foo"
        SymoneResponse.check_modifier_command_attributes(aspect, value)


def test_check_modifier_command_attributes_raises_when_mismatched_types():
    with pytest.raises(AttributeError):
        aspect = Aspect("bar", "", "", value_type=str)
        value = 1
        SymoneResponse.check_modifier_command_attributes(aspect, value)


def test_init_rejects_nonetype_command():
    with pytest.raises(AttributeError):
        SymoneResponse(None)


@pytest.mark.parametrize("aspect_type,value", [(str, 1), (int, "test"), (None, 1)])
def test_init_rejects_incorrect_aspect_value(aspect_type, value):
    with pytest.raises(AttributeError):
        SymoneResponse(
            command_dict.get("current"),
            aspect=Aspect("bar", "", "", value_type=aspect_type),
            value=value,
        )


def test_get_with_value():
    def sub_func(value, **kwargs):
        return Response(value, 200)

    response = SymoneResponse(
        Command("foo", "", sub_func, is_modifier=True),
        aspect=Aspect("bar", "", "", value_type=str),
        value="test",
    )

    result = response.get()
    expected = Response("test", 200)
    assert result.status_code == expected.status_code
    assert result.data == expected.data


def test_get_with_only_aspect():
    def sub_func(**kwargs):
        return Response()

    response = SymoneResponse(
        Command("foo", "", sub_func), aspect=Aspect("bar", "", "")
    )

    result = response.get()
    expected = Response()
    assert result.status_code == expected.status_code
    assert result.data == expected.data


def test_reject_non_modifier_commands_with_values():
    with pytest.raises(AttributeError):
        SymoneResponse(
            Command("current", "", current),
            aspect=Aspect("bar", "", "", value_type=str),
            value="foo",
        )


def test_create_response_with_non_modifier_command():
    def sub_func(**kwargs):
        return Response()

    metadata = QueryMetaData("foo")
    response = SymoneResponse(
        Command("current", "", sub_func), metadata, aspect=Aspect("bar", "", "")
    )

    result = response.get()
    expected = Response()
    assert result.status_code == expected.status_code
    assert result.data == expected.data


def test_create_response_with_current_command():
    def sub_func(**kwargs):
        return Response()

    metadata = QueryMetaData("foo")
    response = SymoneResponse(
        Command("current", "get current", sub_func),
        metadata=metadata,
        aspect=aspect_dict.get("xp"),
        value=None,
    )

    result = response.get()
    expected = Response()
    assert result.status_code == expected.status_code
    assert result.data == expected.data
