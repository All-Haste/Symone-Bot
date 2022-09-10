from unittest.mock import MagicMock

from flask import Request

from main import symone_message
from symone_bot.commands import MESSAGE_RESPONSE_EPHEMERAL


def test_symone_message():
    test_input = {"text": "foo+bar+baz", "user_id": "foo"}

    expected = {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": "I am Symone Bot. I keep track of party gold, XP, and loot. Type `/symone help` to see what I can do.",
    }
    actual = symone_message(test_input)
    assert actual["response_type"] == expected["response_type"]
    assert actual["text"] == expected["text"]


def test_symone_message_blank_input():
    test_input = {"user_id": "foo"}

    expected = {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": "I am Symone Bot. I keep track of party gold, XP, and loot. Type `/symone help` to see what I can do.",
    }
    actual = symone_message(test_input)
    assert actual["response_type"] == expected["response_type"]
    assert actual["text"] == expected["text"]
