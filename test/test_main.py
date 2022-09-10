from unittest.mock import MagicMock

from flask import Request

from main import symone_message
from symone_bot.commands import MESSAGE_RESPONSE_EPHEMERAL
from symone_bot.HandlerSource import HandlerSource


def test_symone_message():
    test_input = "foo+bar+baz"
    user = "foo"

    expected = {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": "I'm sorry, I don't understand.",
    }
    actual = symone_message(test_input, user, HandlerSource.ASPECT_QUERY)
    assert actual["response_type"] == expected["response_type"]
    assert actual["text"] == expected["text"]


def test_symone_message_no_user_id():
    expected = {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": "Sorry, Slack told me your user ID is blank? That's weird. Please try again.",
    }
    actual = symone_message(None, None, None)
    assert actual["response_type"] == expected["response_type"]
    assert actual["text"] == expected["text"]
