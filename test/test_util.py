from symone_bot.util import mocking_spongebob_reply


def test_mocking_spongebob_reply():
    message = {"text": "Did we level up?"}
    reply = mocking_spongebob_reply(message)
    assert reply == ':spongebob-mocking: "DiD We lEvEl uP?" :spongebob-mocking:'
