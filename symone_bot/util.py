import random
from typing import Dict


def mocking_spongebob_reply(message):
    """
    Returns a mocking spongebob reply.

    param message: message received from Slack
    return: mocking spongebob reply
    """
    original_text = message.get("text")
    mocking_text = "".join(
        [x.lower() if i % 2 else x.upper() for i, x in enumerate(original_text)]
    )
    reply = f':spongebob-mocking: "{mocking_text}" :spongebob-mocking:'
    return reply


def get_mocking_reply(message: Dict[str, str]) -> str:
    """
    Returns a mocking reply. It is annoying when the players ask if they've leveled up every session.

    param message: message received from Slack.
    return: a mocking reply.
    """
    return random.choice(
        [
            mocking_spongebob_reply(message),
            "No :arms_crossed:",
            "Calculating... :thinking_face: ... ... :hmmplus: ... :warning: WARNING XP TOO HIGH, REDUCING TO 0 :warning:",
            "I don't know, did you?",
        ]
    )
