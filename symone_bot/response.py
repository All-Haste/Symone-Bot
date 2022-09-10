from typing import Any, Dict

from symone_bot.aspects import Aspect
from symone_bot.commands import Command
from symone_bot.metadata import QueryMetaData


class SymoneResponse:
    """
    Object encapsulating a command, aspect, and value (where applicable).
    SymoneResponse is meant to be the final piece that can create the data
    needed for the bot to respond to the user.
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
        self.value = value

    def get(self) -> Dict[str, str]:
        """
        Executes the response's stored Command callable.
        :return: Dictionary representing a slack message.
        """
        if self.aspect is not None and self.aspect.value_type is not None:
            # execute command on aspect with value
            return self.command.callable(self.metadata, self.aspect, self.value)
        elif self.aspect is not None and self.aspect.value_type is None:
            # execute command on aspect (has no value)
            return self.command.callable(self.metadata, self.aspect)
        else:
            return self.command.callable(self.metadata)
