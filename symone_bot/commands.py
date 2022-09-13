import logging
from functools import wraps
from typing import Any, Callable, Dict

from symone_bot.aspects import Aspect, aspect_dict
from symone_bot.data import DatabaseClient

from symone_bot.metadata import QueryMetaData

MESSAGE_RESPONSE_CHANNEL = "in_channel"
MESSAGE_RESPONSE_EPHEMERAL = "ephemeral"


# TODO bot functions:
# Any add loot
# Did they level?
# Set next level (plus set xp... might avoid having to build an xp table..)


def game_master_only(f: Callable) -> Callable:
    """
    Decorator to check if the user is the game master before executing the command.
    param f: Callable to be decorated.
    return: Callable to be executed, or a default response if the user is not the game master.
    """

    @wraps(f)
    def wrapper(*args):
        metadata: QueryMetaData = args[0]
        aspect = args[1]

        database_client = DatabaseClient.get_client()
        if metadata.user_id != database_client.get_game_master():
            logging.warning(
                f"Unauthorized user attempted to execute add command on {aspect.name} Aspect."
            )
            return {
                "response_type": MESSAGE_RESPONSE_CHANNEL,
                "text": "Nice try...",
            }
        else:
            return f(*args)

    return wrapper


def no_singleton_aspects(f: Callable) -> Callable:
    """
    Decorator to check if the aspect is a singleton before executing the command.
    param f: Callable to be decorated.
    return: Callable to be executed, or a default response if the aspect is a singleton.
    """

    @wraps(f)
    def wrapper(*args):
        aspect = args[1]

        if aspect.is_singleton:
            return {
                "response_type": MESSAGE_RESPONSE_CHANNEL,
                "text": f"{aspect.name} is a singleton aspect, you can't add to it.",
            }
        else:
            return f(*args)

    return wrapper


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


def default_response(metadata: QueryMetaData, **kwargs) -> dict:
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


def help_message(metadata: QueryMetaData, **kwargs) -> dict:
    """
    Auto generates help message by gathering the help info from each SymoneCommand.

    param metadata: QueryMetaData object containing the metadata for the request.
    return: dict containing the response to be sent to Slack.
    """
    logging.info(f"Default response triggered by user: {metadata.user_id}")
    text = """"""
    for command in command_dict.values():
        if not command.callable == default_response:
            text += f"{command.help()}\n"
    text += f"\nI am also tracking the following aspects: {', '.join([aspect.name for aspect in aspect_dict.values()])}"
    return {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": text,
    }


@game_master_only
@no_singleton_aspects
def add(
    metadata: QueryMetaData, aspect: Aspect, value: Any, **kwargs
) -> Dict[str, str]:
    """
    Adds the value to the aspect value stored in the database.

    param metadata: QueryMetaData object containing the metadata for the request.
    param aspect: Aspect object containing the aspect to be modified.
    param value: Value to be added to the aspect.
    return: dict containing the response to be sent to Slack.
    """
    logging.info(f"Add triggered by user: {metadata.user_id}")
    database_client = DatabaseClient.get_client()

    campaign = database_client.get_current_campaign()
    current_aspect_value = campaign[aspect.database_key]
    if aspect.sub_database_key:
        current_aspect_value = current_aspect_value[aspect.sub_database_key]
    new_aspect_value = current_aspect_value + value
    campaign[aspect.name] = new_aspect_value
    database_client.update_game_context(campaign)

    logging.info(f"Updated {aspect.name} to {new_aspect_value}")

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"Updated {aspect.name} to {new_aspect_value}",
    }


def current(metadata: QueryMetaData, aspect: Aspect, **kwargs) -> Dict[str, str]:
    """
    Gets the current aspect value.

    param metadata: QueryMetaData object containing the metadata for the request.
    param aspect: Aspect object containing the aspect to be modified.
    return: dict containing the response to be sent to Slack.
    """
    database_client = DatabaseClient.get_client()
    logging.info(f"Current triggered by user: {metadata.user_id}")
    campaign = database_client.get_current_campaign()

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"{aspect.name} is currently {campaign[aspect.name]}",
    }


@game_master_only
@no_singleton_aspects
def remove(
    metadata: QueryMetaData, aspect: Aspect, value: Any, **kwargs
) -> Dict[str, str]:
    """
    Removes the value amount from the aspect.

    param metadata: QueryMetaData object containing the metadata for the request.
    param aspect: Aspect object containing the aspect to be modified.
    param value: Value to be removed from the aspect.
    return: dict containing the response to be sent to Slack.
    """
    database_client = DatabaseClient.get_client()
    logging.info(f"Remove triggered by user: {metadata.user_id}")

    campaign = database_client.get_current_campaign()

    current_aspect_value = campaign[aspect.name]
    new_aspect_value = current_aspect_value - value
    campaign[aspect.name] = new_aspect_value
    database_client.update_game_context(campaign)

    logging.info(f"Updated {aspect.name} to {new_aspect_value}")

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"Reduced {aspect.name} to {new_aspect_value}",
    }


def switch_campaign(metadata: QueryMetaData, aspect: str, **kwargs) -> Dict[str, str]:
    """
    Switches the campaign to the one specified.

    param metadata: QueryMetaData object containing the metadata for the request.
    param campaign_name: Name of the campaign to switch to.
    return: dict containing the response to be sent to Slack.
    """
    database_client = DatabaseClient.get_client()
    logging.info(
        f"Switch campaign triggered by user: {metadata.user_id}, campaign: '{aspect}'"
    )

    try:
        found_campaign = database_client.get_context_by_campaign_name(aspect)
    except Exception as e:
        logging.error(f"Error finding campaign: {aspect}")
        logging.exception(e)
        return {
            "response_type": MESSAGE_RESPONSE_CHANNEL,
            "text": f"Error finding campaign: {e}",
        }
    current_campaign = database_client.get_current_context_id()
    current_campaign["campaign_id"] = found_campaign.key.id_or_name
    database_client.update_game_context(current_campaign)

    logging.info(f"Current campaign set to {aspect}")

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"Current campaign set to {aspect}",
    }


def strange(**kwargs) -> Dict[str, str]:
    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": "Strange things are afoot at the Circle K.",
    }


# List of commands used to build out
command_dict: Dict[str, Command] = {
    "default": Command("default", "", default_response),
    "help": Command("help", "retrieves help info", help_message),
    "add": Command(
        "add", "adds a given value to a given aspect.", add, is_modifier=True
    ),
    "current": Command(
        "current",
        "retrieves the current value of a given aspect.",
        current,
        is_modifier=False,
    ),
    "remove": Command(
        "remove", "removes a given value from a given aspect.", remove, is_modifier=True
    ),
    "switch campaign to": Command(
        "switch campaign to",
        "switches the current campaign.",
        switch_campaign,
        is_modifier=True,
    ),
    "movie quote please": Command(
        "movie quote please", "retrieves a strange response", strange
    ),
}
