import os
from typing import Dict, Callable, List
from google.cloud import datastore

GAME_MASTER = os.getenv('GAME_MASTER')
PROJECT_ID = os.getenv("PROJECT_ID")
MESSAGE_RESPONSE_CHANNEL = "in_channel"
MESSAGE_RESPONSE_EPHEMERAL = "ephemeral"

DATA_KEY_CAMPAIGN = "campaign"


# TODO bot functions:
# GM add xp
# GM add gold
# Any add loot
# Did they level?
# Set next level (plus set xp... might avoid having to build an xp table..)


def create_client(project_id: str):
    return datastore.Client(project_id)


class SymoneCommand:
    def __init__(self, query: str, help_info: str, function: Callable):
        self.query = query
        self.help_info = help_info
        if not callable(function):
            raise AttributeError(f"'function' must be type Callable.")
        self.callable = function

    def get_response(self, *args) -> Dict[str, str]:
        print(f"{self.query} called, executing.")
        return self.callable(*args)

    def help(self) -> str:
        return f"`{self.query}`: {self.help_info}."


def default_response(*args) -> dict:
    return {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": "I am Symone Bot. I keep track of party gold, XP, and loot. Type `/symone help` to see what I can do."
    }


def help_message(*args) -> dict:
    """Auto generates help message by gathering the help info from each SymoneCommand."""
    text = """"""
    for command in commands:
        if not command.callable == default_response:
            text += f"{command.help()}\n"
    return {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": text,
    }


def current_xp(*args) -> dict:
    datastore_client = create_client(PROJECT_ID)
    query = datastore_client.query(kind="campaign").fetch()
    result = query.next()
    party_xp = result["xp"]
    party_size = result["party_size"]
    xp_for_next_level = result["xp_target"]
    xp_left = xp_for_next_level * party_size - party_xp

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"""The party has amassed {party_xp} XP.
Next level is achieved at {xp_for_next_level} XP per character for a total of {xp_for_next_level * party_size}.
The party needs {xp_left} to reach next level.""",
    }


def add_xp(*args):
    user = args[0][0]
    if user != GAME_MASTER:
        print(f"{user} != {GAME_MASTER}")
        return {
            "response_type": MESSAGE_RESPONSE_CHANNEL,
            "text": f"Nice try...",
        }
    xp_to_add = args[0][1]
    datastore_client = create_client(PROJECT_ID)
    query = datastore_client.query(kind="campaign").fetch()
    result = query.next()
    party_xp = result["xp"]
    new_xp = party_xp + xp_to_add
    result["xp"] = new_xp
    datastore_client.put(result)

    print(f"Updated party xp to {new_xp}")

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"Updated party xp to {new_xp}",
    }


# List of commands used to build out
commands: List[SymoneCommand] = [
    SymoneCommand("default", "", default_response),
    SymoneCommand("help", "retrieves help info", help_message),
    SymoneCommand("xp stats", "gets xp info for the party", current_xp),
    SymoneCommand("add xp", "adds xp to the party total", add_xp),
]
