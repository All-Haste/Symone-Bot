from typing import Any, Dict

from symone_bot.aspects import Aspect
from symone_bot.commands import Command
from symone_bot.metadata import QueryMetaData


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
        aspect: Aspect = None,
        value: Any = None,
    ):
        if command is None:
            raise AttributeError("'command' cannot be type 'NoneType'")
        self.metadata = metadata
        self.command = command
        self.aspect = aspect
        if self.command.is_modifier:
            self.check_modifier_command_attributes(self.aspect, value)
        elif not self.command.is_modifier and command.name != "default":
            if value is not None:
                raise AttributeError("Cannot have a value for a non-modifier command.")
        self.value = value

    @staticmethod
    def check_modifier_command_attributes(aspect, value):
        """
        Checks that the aspect and value are valid for a modifier command.

        param aspect: Aspect object.
        param value: Value to be set for the aspect.
        """
        if aspect.value_type is None and value is not None:
            raise AttributeError(
                f"Aspect value type ({aspect.value_type}) does not match supplied type ({type(value)})"
            )
        if aspect.value_type is not None and not isinstance(value, aspect.value_type):
            raise AttributeError(
                f"Aspect value type ({aspect.value_type}) does not match supplied type ({type(value)})"
            )

    def get(self) -> Dict[str, str]:
        """
        Executes the response's stored Command callable.

        :return: Dictionary representing a Slack message.
        """
        if self.command.is_modifier:
            # execute command on aspect with value
            return self.command.callable(self.metadata, self.aspect, self.value)
        elif self.aspect is not None:
            # execute command on aspect (has no value)
            return self.command.callable(self.metadata, self.aspect)
        else:
            return self.command.callable(self.metadata)
