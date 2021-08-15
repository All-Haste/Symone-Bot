import logging
import os
from typing import Dict, Callable, List, Any
from google.cloud import datastore

from symone_bot.aspects import Aspect
from symone_bot.metadata import QueryMetaData

GAME_MASTER = os.getenv("GAME_MASTER")
PROJECT_ID = os.getenv("PROJECT_ID")
MESSAGE_RESPONSE_CHANNEL = "in_channel"
MESSAGE_RESPONSE_EPHEMERAL = "ephemeral"

DATA_KEY_CAMPAIGN = "campaign"


# TODO bot functions:
# GM add gold
# Any add loot
# Did they level?
# Set next level (plus set xp... might avoid having to build an xp table..)


def create_client(project_id: str):
    return datastore.Client(project_id)


class Command:
    """
    Wrapper around a callable that returns a Flask Response object.
    This wrapper exists to add metadata to the callable.
    """

    def __init__(self, name: str, help_info: str, function: Callable, aspect_type=None):
        self.name = name
        self.help_info = help_info
        if not callable(function):
            raise AttributeError("'function' must be type Callable.")
        self.callable = function
        self.aspect_type = aspect_type

    def help(self) -> str:
        return f"`{self.name}`: {self.help_info}."


def default_response() -> dict:
    return {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": "I am Symone Bot. I keep track of party gold, XP, and loot. Type `/symone help` to see what I can do.",
    }


def help_message() -> dict:
    """Auto generates help message by gathering the help info from each SymoneCommand."""
    text = """"""
    for command in command_list:
        if not command.callable == default_response:
            text += f"{command.help()}\n"
    return {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": text,
    }


def current_xp() -> dict:
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


def add(metadata: QueryMetaData, aspect: Aspect, value: Any) -> Dict[str, str]:
    if metadata.user_id not in aspect.allowed_users:
        logging.warning(
            f"Unauthorized user attempted to execute add command on {aspect.name} Aspect."
        )
        return {
            "response_type": MESSAGE_RESPONSE_CHANNEL,
            "text": "Nice try...",
        }

    datastore_client = create_client(PROJECT_ID)
    query = datastore_client.query(kind="campaign").fetch()
    result = query.next()

    party_xp = result[aspect.name]
    new_xp = party_xp + value
    result[aspect.name] = new_xp
    datastore_client.put(result)

    logging.info(f"Updated {aspect.name} to {new_xp}")

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"Updated {aspect.name} to {new_xp}",
    }


# List of commands used to build out
command_list: List[Command] = [
    Command("default", "", default_response),
    Command("help", "retrieves help info", help_message),
    Command("xp stats", "gets xp info for the party", current_xp),
    Command("add", "adds a given value to a given aspect.", add),
]
