from typing import Type


class Aspect:
    """
    An aspect is a piece of the bot system that commands can be executed on.
    It is worth noting that an aspect's name will also represent a key under
    a 'campaign' document kind stored in the document DB.

    E.G. XP would be an aspect. Calling `add xp 100` means to:
        add(command) xp(aspect) 100(value)
    """

    def __init__(self, name, help_info, value_type: Type = None):
        self.name = name
        self.help_info = help_info
        self.value_type = value_type

    def help(self) -> str:
        return f"`{self.name}`: {self.help_info}."


aspect_list = [Aspect("xp", "experience points")]
