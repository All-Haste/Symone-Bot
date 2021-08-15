from main import parse_slack_data, symone_message
from symone_bot.symone_command import MESSAGE_RESPONSE_EPHEMERAL


def test_parse_slack_data():
    test_input = b"foo=bar&cat=feline&123=easyasabc"
    actual = parse_slack_data(test_input)

    assert actual["foo"] == "bar"
    assert actual["cat"] == "feline"
    assert actual["123"] == "easyasabc"


def test_symone_message():
    test_input = {"text": "foo+bar+baz"}

    expected = {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": "I am Symone Bot. I keep track of party gold, XP, and loot. Type `/symone help` to see what I can do.",
    }
    actual = symone_message(test_input)
    assert actual["response_type"] == expected["response_type"]
    assert actual["text"] == expected["text"]

