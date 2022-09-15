import logging
from functools import wraps
from typing import Any, Callable, Dict, Union

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
    def wrapper(**kwargs):
        metadata: QueryMetaData = kwargs["metadata"]
        aspect = kwargs["aspect"]

        database_client = DatabaseClient.get_client()
        if metadata.user_id != database_client.get_game_master():
            logging.warning(
                f"Unauthorized user attempted to execute add command on {aspect.name if aspect else 'unknown'} Aspect."
            )
            return {
                "response_type": MESSAGE_RESPONSE_CHANNEL,
                "text": "Nice try...",
            }
        else:
            return f(**kwargs)

    return wrapper


def no_singleton_aspects(f: Callable) -> Callable:
    """
    Decorator to check if the aspect is a singleton before executing the command.
    param f: Callable to be decorated.
    return: Callable to be executed, or a default response if the aspect is a singleton.
    """

    @wraps(f)
    def wrapper(**kwargs):
        aspect = kwargs["aspect"]

        if aspect.is_singleton:
            return {
                "response_type": MESSAGE_RESPONSE_CHANNEL,
                "text": f"{aspect.name} is a singleton aspect, you can't call `{f.__name__}` on it.",
            }
        else:
            return f(**kwargs)

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
        if command.callable != default_response:
            text += f"{command.help()}\n"
    text += f"\nI am also tracking the following aspects: {', '.join([aspect.name for aspect in aspect_dict.values()])}"
    return {
        "response_type": MESSAGE_RESPONSE_EPHEMERAL,
        "text": text,
    }


def _compute_new_value(current_aspect_value, value, operator):
    """
    Computes the new value for an aspect.

    param current_aspect_value: Current value of the aspect.
    param value: Value to be added or subtracted.
    param operator: Operator to be used to compute the new value.
    return: New value for the aspect.
    """
    if operator == "+":
        return current_aspect_value + value
    elif operator == "-":
        return current_aspect_value - value
    else:
        raise ValueError("Operator must be either '+' or '-'.")


def _add_and_remove_handler(
    aspect: Aspect, value: Union[str, int], operator: str
) -> Union[str, int]:
    """
    Handles the logic for adding and removing values from aspects.

    param aspect: aspect to be modified.
    param value: value to be added or removed.
    param operator: operator to be used to compute the new value.
    return: new value for the aspect.
    """
    if operator not in ["+", "-"]:
        raise ValueError("Operator must be either '+' or '-'.")
    database_client = DatabaseClient.get_client()

    game_context = database_client.get_current_game_context()

    if aspect.sub_database_key:
        current_aspect_value = game_context[aspect.database_key][
            aspect.sub_database_key
        ]
        new_aspect_value = _compute_new_value(current_aspect_value, value, operator)
        game_context[aspect.database_key][aspect.sub_database_key] = new_aspect_value
    else:
        current_aspect_value = game_context[aspect.database_key]
        new_aspect_value = _compute_new_value(current_aspect_value, value, operator)
        game_context[aspect.database_key] = new_aspect_value

    database_client.update_game_context(game_context)
    return new_aspect_value


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
    response = {}
    logging.info(f"Add triggered by user: {metadata.user_id}")
    new_aspect_value = _add_and_remove_handler(aspect, value, "+")
    if aspect.name == "xp":
        response = compute_level_up(new_aspect_value, response)

    logging.info(f"Updated {aspect.name} to {new_aspect_value}")

    if not response:
        response = {
            "response_type": MESSAGE_RESPONSE_CHANNEL,
            "text": f"Updated {aspect.name} to {new_aspect_value}",
        }
    return response


def compute_level_up(new_aspect_value, response):
    database_client = DatabaseClient.get_client()
    game_context = database_client.get_current_game_context()
    party = game_context["party"]
    level = party["level"]
    xp_target = party["xp_for_level_up"]
    if new_aspect_value >= xp_target:
        game_context["party"]["level"] = level + 1
        database_client.update_game_context(game_context)
        response = {
            "response_type": MESSAGE_RESPONSE_CHANNEL,
            "text": f"Updated xp to {new_aspect_value}. The party leveled up! :tada: You're now level {level + 1}!",
        }
    return response


def current(metadata: QueryMetaData, aspect: Aspect, **kwargs) -> Dict[str, str]:
    """
    Gets the current aspect value.

    param metadata: QueryMetaData object containing the metadata for the request.
    param aspect: Aspect object containing the aspect to be modified.
    return: dict containing the response to be sent to Slack.
    """
    database_client = DatabaseClient.get_client()
    logging.info(f"Current triggered by user: {metadata.user_id}")
    campaign = database_client.get_current_game_context()

    current_value = campaign[aspect.database_key]
    if aspect.sub_database_key:
        current_value = current_value[aspect.sub_database_key]
    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"{aspect.name} is currently {current_value}",
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
    logging.info(f"Remove triggered by user: {metadata.user_id}")
    new_aspect_value = _add_and_remove_handler(aspect, value, "-")
    logging.info(f"Updated {aspect.name} to {new_aspect_value}")

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"Reduced {aspect.name} to {new_aspect_value}",
    }


@game_master_only
def set_aspect(
    metadata: QueryMetaData, aspect: Aspect, value: Union[str, int], **kwargs
) -> Dict[str, str]:
    """
    Sets the aspect to the supplied value.

    param metadata: QueryMetaData object containing the metadata for the request.
    param value: Value to set the aspect to.
    return: dict containing the response to be sent to Slack.
    """
    database_client = DatabaseClient.get_client()
    logging.info(f"Set triggered by user: {metadata.user_id}")

    game_context = database_client.get_current_game_context()

    if aspect.sub_database_key:
        game_context[aspect.database_key][aspect.sub_database_key] = value
    else:
        game_context[aspect.database_key] = value
    database_client.update_game_context(game_context)

    logging.info(f"Updated {aspect.name} to {value}")

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"Set {aspect.name} to {value}",
    }


def switch_campaign(metadata: QueryMetaData, value: str, **kwargs) -> Dict[str, str]:
    """
    Switches the campaign to the one specified.

    param metadata: QueryMetaData object containing the metadata for the request.
    param value: Name of the campaign to switch to.
    return: dict containing the response to be sent to Slack.
    """
    database_client = DatabaseClient.get_client()
    logging.info(
        f"Switch campaign triggered by user: {metadata.user_id}, campaign: '{value}'"
    )

    try:
        found_campaign = database_client.get_context_by_campaign_name(value)
    except Exception as e:
        logging.error(f"Error finding campaign: {value}")
        logging.exception(e)
        return {
            "response_type": MESSAGE_RESPONSE_CHANNEL,
            "text": f"Error finding campaign: `{value}`, make sure case is correct.",
        }
    database_client.update_active_game_context(found_campaign["_id"])

    logging.info(f"Current campaign set to {value}")

    return {
        "response_type": MESSAGE_RESPONSE_CHANNEL,
        "text": f"Current campaign set to {value}",
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
    "set": Command(
        "set", "sets a given aspect to a given value.", set_aspect, is_modifier=True
    ),
    "switch campaign to": Command(
        "switch campaign to",
        "switches the current campaign.",
        switch_campaign,
        is_modifier=True,
    ),
}
