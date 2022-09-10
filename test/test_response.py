import pytest
from flask import Response

from symone_bot.aspects import Aspect
from symone_bot.commands import Command, command_list, current
from symone_bot.metadata import QueryMetaData
from symone_bot.response import SymoneResponse


def test_init_rejects_nonetype_command():
    with pytest.raises(AttributeError):
        SymoneResponse(None)


@pytest.mark.parametrize("aspect_type,value", [(str, 1), (int, "test"), (None, 1)])
def test_init_rejects_incorrect_aspect_value(aspect_type, value):
    with pytest.raises(AttributeError):
        SymoneResponse(
            command_list[2],
            aspect=Aspect("bar", "", value_type=aspect_type),
            value=value,
        )


def test_get_with_value():
    def sub_func(metadata, aspect, value):
        return Response(value, 200)

    response = SymoneResponse(
        Command("foo", "", sub_func, is_modifier=True),
        aspect=Aspect("bar", "", value_type=str),
        value="test",
    )

    result = response.get()
    expected = Response("test", 200)
    assert result.status_code == expected.status_code
    assert result.data == expected.data


def test_get_with_only_aspect():
    def sub_func(metadata, aspect):
        return Response()

    response = SymoneResponse(Command("foo", "", sub_func), aspect=Aspect("bar", ""))

    result = response.get()
    expected = Response()
    assert result.status_code == expected.status_code
    assert result.data == expected.data


def test_reject_non_modifier_commands_with_values():
    with pytest.raises(AttributeError):
        SymoneResponse(
            Command("current", "", current),
            aspect=Aspect("bar", "", value_type=str),
            value="foo",
        )


def test_create_response_with_current_command():
    def sub_func(metadata, aspect):
        return Response()

    metadata = QueryMetaData("foo")
    response = SymoneResponse(
        Command("current", "", sub_func), metadata, aspect=Aspect("bar", "")
    )

    result = response.get()
    expected = Response()
    assert result.status_code == expected.status_code
    assert result.data == expected.data
