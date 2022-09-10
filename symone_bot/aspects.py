import os
from typing import List, Type

GAME_MASTER = os.getenv("GAME_MASTER")


class Aspect:
    """
    An aspect is a piece of the bot system that commands can be executed on.
    It is worth noting that an aspect's name will also represent a key under
    a 'campaign' document kind stored in the document DB.

    E.G. XP would be an aspect. Calling `add xp 100` means to:
        add(command) xp(aspect) 100(value)
    """

    def __init__(
        self, name: str, help_info: str, value_type: Type = None, allowed_users=None
    ):
        if allowed_users is None:
            allowed_users = [GAME_MASTER]
        self.name = name
        self.help_info = help_info
        self.value_type = value_type
        self.allowed_users = allowed_users

    def help(self) -> str:
        return f"`{self.name}`: {self.help_info}."


aspect_list: List[Aspect] = [
    Aspect("xp", "experience points", value_type=int),
    Aspect("target_xp", "target experience points", value_type=int),
    Aspect("gold", "gold pieces", value_type=int),
    Aspect("party_size", "party size", value_type=int),
]
