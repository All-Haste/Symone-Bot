import pytest

from main import parse_slack_data, help_message, default_response, response_switch, MESSAGE_RESPONSE_EPHEMERAL, \
    symone_message


def test_parse_slack_data():
    test_input = b"foo=bar&cat=feline&123=easyasabc"
    actual = parse_slack_data(test_input)

    assert actual["foo"] == "bar"
    assert actual["cat"] == "feline"
    assert actual["123"] == "easyasabc"


@pytest.mark.parametrize("query,response_callable", [
    ("jfkdla;jkfd", default_response),
    ("help", help_message),
])
def test_response_switch(query, response_callable):
    actual = response_switch(query)
    assert actual == response_callable


def test_symone_message():
    test_input = {"text": "foo+bar+baz"}

    expected = {"response_type": MESSAGE_RESPONSE_EPHEMERAL,
                "text": "I am Symone Bot. I keep track of party gold, XP, and loot. Type `/symone help` to see what I can do."}
    actual = symone_message(test_input)
    assert actual["response_type"] == expected["response_type"]
    assert actual["text"] == expected["text"]
