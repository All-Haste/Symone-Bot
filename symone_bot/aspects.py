import os
from typing import Type, Dict

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
        self,
        name: str,
        help_info: str,
        database_key: str,
        sub_database_key: str = None,
        value_type: Type = None,
        allowed_users=None,
        is_singleton=False,
    ):
        self.name = name
        self.help_info = help_info
        self.database_key = database_key
        self.sub_database_key = sub_database_key
        self.value_type = value_type
        self.allowed_users = allowed_users
        self.is_singleton = is_singleton

    def __str__(self):
        return self.name

    def help(self) -> str:
        return f"`{self.name}`: {self.help_info}."


# TODO: implment a mapping of aspect name to database property, so that users can use natural language
# example: "party size" -> "party_size", "experience points" -> "xp", etc.
aspect_dict: Dict[str, Aspect] = {
    "xp": Aspect(
        "xp", "experience points", "party", sub_database_key="xp", value_type=int
    ),
    "xp_target": Aspect(
        "xp_target",
        "target experience points",
        "party",
        sub_database_key="xp_for_level_up",
        value_type=int,
    ),
    "gold": Aspect(
        "gold", "gold pieces", "currency", sub_database_key="quantity", value_type=int
    ),
    "party_size": Aspect(
        "party_size", "party size", "party", sub_database_key="size", value_type=int
    ),
    "campaign": Aspect(
        "campaign", "campaign name", "name", value_type=str, is_singleton=True
    ),
}
