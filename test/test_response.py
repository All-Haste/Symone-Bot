import pytest
from flask import Response

from symone_bot.aspects import Aspect
from symone_bot.commands import Command
from symone_bot.response import SymoneResponse


def test_init_rejects_nonetype_command():
    with pytest.raises(AttributeError):
        SymoneResponse(None)


@pytest.mark.parametrize("aspect_type,value", [(str, 1), (int, "test"), (None, 1)])
def test_init_rejects_incorrect_aspect_value(aspect_type, value):
    with pytest.raises(AttributeError):
        SymoneResponse(
            Command("foo", "", lambda: Response()),
            aspect=Aspect("bar", "", value_type=aspect_type),
            value=value,
        )


def test_get_happy_path():
    response = SymoneResponse(Command("foo", "", lambda: Response()), value="test")

    result = response.get()

    assert result.status_code == Response().status_code


def test_get():
    def sub_func(aspect, value):
        return Response(value, 200)

    response = SymoneResponse(
        Command("foo", "", sub_func),
        aspect=Aspect("bar", "", value_type=str),
        value="test",
    )

    result = response.get()
    expected = Response("test", 200)
    assert result.status_code == expected.status_code
    assert result.data == expected.data
