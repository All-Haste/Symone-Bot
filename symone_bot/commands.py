import logging
import os
from typing import Any, Callable, Dict, List

from symone_bot.aspects import Aspect, aspect_list
from symone_bot.data import DatabaseClient


from symone_bot.metadata import QueryMetaData

PROJECT_ID = os.getenv("PROJECT_ID", "test-project")
MESSAGE_RESPONSE_CHANNEL = "in_channel"
MESSAGE_RESPONSE_EPHEMERAL = "ephemeral"

# TODO bot functions:
# Any add loot
# Did they level?
# Set next level (plus set xp... might avoid having to build an xp table..)

database_client = DatabaseClient(PROJECT_ID)


class Command:
    """
    Wrapper around a callable that returns a Flask Response object.
    This wrapper exists to add metadata to the callable.

    Attributes:
        name: Name of the command.
        help_info: Help information for the command.
        function: Callable to be wrapped.
        aspect_type: Aspect type that the command is associated with.
        is_modifier: Whether the command is a modifier.
    """

    def __init__(
        self,
        name: str,
        help_info: str,
        function: Callable,
        aspect_type: Aspect = None,
        is_modifier: bool = False,
    ):
        self.name = name
        self.help_info = help_info
        if not callable(function):
            raise AttributeError("'function' must be type Callable.")
        self.callable = function
        self.aspect_type = aspect_type
        self.is_modifier = is_modifier

    def __str__(self):
        return self.name

    def help(self) -> str:
        return f"`{self.name}`: {self.help_info}."


def default_response(metadata: QueryMetaData) -> dict:
    """
    Default response for when a command is not recognized.

    param metadata: QueryMetaData object containing the metadata for the request.
    return: dict containing the response to be sent to Slack.
    """
    logging.info(f"Default response triggered by user: {metadata.user_id}")
    return {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": "I'm sorry, I don't understand.",
    }


def help_message(metadata: QueryMetaData) -> dict:
    """
    Auto generates help message by gathering the help info from each SymoneCommand.

    param metadata: QueryMetaData object containing the metadata for the request.
    return: dict containing the response to be sent to Slack.
    """
    logging.info(f"Default response triggered by user: {metadata.user_id}")
    text = """"""
    for command in command_list:
        if not command.callable == default_response:
            text += f"{command.help()}\n"
    text += f"\nI am also tracking the following aspects: {', '.join([aspect.name for aspect in aspect_list])}"
    return {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": text,
    }


def add(metadata: QueryMetaData, aspect: Aspect, value: Any) -> Dict[str, str]:
    """
    Adds the value to the aspect value stored in GCP Datastore

    param metadata: QueryMetaData object containing the metadata for the request.
    param aspect: Aspect object containing the aspect to be modified.
    param value: Value to be added to the aspect.
    return: dict containing the response to be sent to Slack.
    """
    logging.info(f"Add triggered by user: {metadata.user_id}")
    if metadata.user_id != database_client.get_game_master():
        logging.warning(
            f"Unauthorized user attempted to execute add command on {aspect.name} Aspect."
        )
        return {
            "response_type": MESSAGE_RESPONSE_CHANNEL,
            "text": "Nice try...",
        }

    if aspect.is_singleton:
        return {
            "response_type": MESSAGE_RESPONSE_CHANNEL,
            "text": f"{aspect.name} is a singleton aspect, you can't add to it.",
        }

    campaign = database_client.get_current_campaign()
    current_aspect_value = campaign[aspect.name]
    new_aspect_value = current_aspect_value + value
    campaign[aspect.name] = new_aspect_value
    database_client.put_record(campaign)

    logging.info(f"Updated {aspect.name} to {new_aspect_value}")

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"Updated {aspect.name} to {new_aspect_value}",
    }


def current(metadata: QueryMetaData, aspect: Aspect) -> Dict[str, str]:
    """
    Gets the current aspect value stored in GCP Datastore

    param metadata: QueryMetaData object containing the metadata for the request.
    param aspect: Aspect object containing the aspect to be modified.
    """
    logging.info(f"Current triggered by user: {metadata.user_id}")
    campaign = database_client.get_current_campaign()

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"{aspect.name} is currently {campaign[aspect.name]}",
    }


# remove and add can probably be combined to the same core command, with a switch for +/-
def remove(metadata: QueryMetaData, aspect: Aspect, value: Any) -> Dict[str, str]:
    """
    Removes the value from the aspect value stored in GCP Datastore

    param metadata: QueryMetaData object containing the metadata for the request.
    param aspect: Aspect object containing the aspect to be modified.
    param value: Value to be removed from the aspect.
    return: dict containing the response to be sent to Slack.
    """
    logging.info(f"Remove triggered by user: {metadata.user_id}")
    if metadata.user_id != database_client.get_game_master():
        logging.warning(
            f"Unauthorized user attempted to execute remove command on {aspect.name} Aspect."
        )
        return {
            "response_type": MESSAGE_RESPONSE_CHANNEL,
            "text": "Nice try...",
        }

    if aspect.is_singleton:
        return {
            "response_type": MESSAGE_RESPONSE_CHANNEL,
            "text": f"{aspect.name} is a singleton aspect, you can't remove from it.",
        }

    campaign = database_client.get_current_campaign()

    current_aspect_value = campaign[aspect.name]
    new_aspect_value = current_aspect_value - value
    campaign[aspect.name] = new_aspect_value
    database_client.put_record(campaign)

    logging.info(f"Updated {aspect.name} to {new_aspect_value}")

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"Reduced {aspect.name} to {new_aspect_value}",
    }


def switch_campaign(metadata: QueryMetaData, campaign_name: str) -> Dict[str, str]:
    """
    Switches the campaign to the one specified.

    param metadata: QueryMetaData object containing the metadata for the request.
    param campaign_name: Name of the campaign to switch to.
    return: dict containing the response to be sent to Slack.
    """
    logging.info(
        f"Switch campaign triggered by user: {metadata.user_id}, campaign: '{campaign_name}'"
    )

    try:
        found_campaign = database_client.get_campaign_by_name(campaign_name)
    except Exception as e:
        logging.error(f"Error finding campaign: {campaign_name}")
        logging.exception(e)
        return {
            "response_type": MESSAGE_RESPONSE_CHANNEL,
            "text": f"Error finding campaign: {e}",
        }
    current_campaign = database_client.get_current_campaign_entity()
    current_campaign["campaign_id"] = found_campaign.key.id_or_name
    database_client.put_record(current_campaign)

    logging.info(f"Current campaign set to {campaign_name}")

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"Current campaign set to {campaign_name}",
    }


def strange(metadata: QueryMetaData) -> Dict[str, str]:
    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": "Strange things are afoot at the Circle K.",
    }


# List of commands used to build out
command_list: List[Command] = [
    Command("default", "", default_response),
    Command("help", "retrieves help info", help_message),
    Command("add", "adds a given value to a given aspect.", add, is_modifier=True),
    Command(
        "current",
        "retrieves the current value of a given aspect.",
        current,
        is_modifier=False,
    ),
    Command(
        "remove", "removes a given value from a given aspect.", remove, is_modifier=True
    ),
    Command(
        "switch campaign to",
        "switches the current campaign.",
        switch_campaign,
        is_modifier=True,
    ),
    Command("movie quote please", "retrieves a strange response", strange),
]
