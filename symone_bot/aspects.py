from typing import Type


class Aspect:
    def __init__(self, name, help_info, value_type: Type = None):
        self.name = name
        self.help_info = help_info
        self.value_type = value_type

    def help(self) -> str:
        return f"`{self.name}`: {self.help_info}."


aspect_list = [Aspect("xp", "foo")]
