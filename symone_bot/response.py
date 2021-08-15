from typing import Callable, Any

from symone_bot.aspects import Aspect
from symone_bot.commands import Command


class SymoneResponse:
    def __init__(self, command: Command, aspect: Aspect = None, value: Any = None):
        self.command = command
        self.aspect = aspect
        if self.aspect is not None:
            if not isinstance(value, self.aspect.value_type):
                raise AttributeError(
                    f"Aspect value type ({self.aspect.value_type}) does not match supplied type ({type(value)})"
                )
        self.value = value

    def get(self):
        if self.aspect is not None and self.aspect.value_type is not None:
            # execute command on aspect with value
            return self.command.callable(self.aspect, self.value)
        elif self.aspect is not None and self.aspect.value_type is None:
            # execute command on aspect (has no value)
            return self.command.callable(self.aspect)
        else:
            return self.command.callable()
