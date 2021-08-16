from unittest.mock import MagicMock

from flask import Request

from main import parse_slack_data, symone_message, verify_signature, symone_bot
from symone_bot.commands import MESSAGE_RESPONSE_EPHEMERAL


def test_verify_signature(mocker):
    environ = mocker.patch("os.environ")
    environ.return_value = {"SLACK_SECRET": "foobar"}
    req = Request(MagicMock())
    actual = verify_signature(req)

    assert actual.status_code == 401


def test_parse_slack_data():
    test_input = b"foo=bar&cat=feline&123=easyasabc"
    actual = parse_slack_data(test_input)

    assert actual["foo"] == "bar"
    assert actual["cat"] == "feline"
    assert actual["123"] == "easyasabc"


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


def test_symone_bot_post_only():
    req = Request(MagicMock())
    req.method = "GET"

    actual = symone_bot(req)
    assert actual.status_code == 405


def test_symone_bot(mocker):
    # note this is a fairly naive test
    mocker.patch("main.verify_signature")
    jsonify_mock = mocker.patch("main.jsonify")
    jsonify_mock.return_value = "foo"
    req = Request(MagicMock())
    req.method = "POST"
    req.data = b"text=foo+bar+baz&user_id=foo"

    actual = symone_bot(req)

    assert actual == "foo"
