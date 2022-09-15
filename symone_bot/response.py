from typing import Any, Dict

from symone_bot.aspects import Aspect
from symone_bot.commands import Command, command_dict
from symone_bot.metadata import QueryMetaData
from symone_bot.prepositions import Preposition


class SymoneResponse:
    """
    Object encapsulating a command, aspect, and value (where applicable).
    SymoneResponse is meant to be the final piece that can create the data
    needed for the bot to respond to the user.

    Attributes:
        command: Command object representing the command to be executed.
        aspect: Aspect object representing the aspect to be modified or fetched.
        value: Value to be used in modifying the aspect.
    """

    def __init__(
        self,
        command: Command,
        metadata: QueryMetaData = None,
        preposition: Preposition = None,
        aspect: Aspect = None,
        value: Any = None,
    ):
        if command is None:
            raise AttributeError("'command' cannot be type 'NoneType'")
        self.metadata = metadata
        self.command = command
        self.preposition = preposition
        self.aspect = aspect

        if self.command.is_modifier:
            if aspect and not aspect.is_singleton:
                self.check_modifier_command_attributes(self.aspect, value)
        elif not self.command.is_modifier and command.name != "default":
            if value is not None:
                raise AttributeError("Cannot have a value for a non-modifier command.")

        self.value = value

    def check_modifier_command_attributes(self, aspect, value):
        """
        Checks that the aspect and value are valid for a modifier command.

        param aspect: Aspect object.
        param value: Value to be set for the aspect.
        """
        if aspect.value_type is None and value is not None:
            self.command = command_dict["default"]
        if aspect.value_type is not None and not isinstance(value, aspect.value_type):
            self.command = command_dict["default"]

    def get(self) -> Dict[str, str]:
        """
        Executes the response's stored Command callable.

        :return: Dictionary representing a Slack message.
        """
        kwargs = {
            "metadata": self.metadata,
            "aspect": self.aspect,
            "value": self.value,
            "preposition": self.preposition,
        }
        return self.command.callable(**kwargs)
