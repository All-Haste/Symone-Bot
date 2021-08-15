from typing import Any

from flask import Response

from symone_bot.aspects import Aspect
from symone_bot.commands import Command


class SymoneResponse:
    """
    Object encapsulating a command, aspect, and value (where applicable).
    SymoneResponse is meant to be the final piece that can create the data
    needed for the bot to respond to the user.
    """

    def __init__(self, command: Command, aspect: Aspect = None, value: Any = None):
        if command is None:
            raise AttributeError("'command' cannot be type 'NoneType'")
        self.command = command
        self.aspect = aspect
        if self.aspect is not None:
            if not isinstance(value, self.aspect.value_type):
                raise AttributeError(
                    f"Aspect value type ({self.aspect.value_type}) does not match supplied type ({type(value)})"
                )
        self.value = value

    def get(self) -> Response:
        """
        Executes the response's stored Command callable.
        :return: Flask response.
        """
        if self.aspect is not None and self.aspect.value_type is not None:
            # execute command on aspect with value
            return self.command.callable(self.aspect, self.value)
        elif self.aspect is not None and self.aspect.value_type is None:
            # execute command on aspect (has no value)
            return self.command.callable(self.aspect)
        else:
            return self.command.callable()
