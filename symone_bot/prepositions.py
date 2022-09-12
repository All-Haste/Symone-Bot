from enum import Enum


class PrepositionType(Enum):
    """Preposition type enum"""

    DIRECTIONAL = 1
    TIME = 2
    PLACE = 3
    LOCATION = 4
    OTHER = 5


class Preposition:
    """Preposition class"""

    def __init__(self, name: str, preposition_type: PrepositionType):
        if not isinstance(name, str):
            raise TypeError("name must be of type str")
        if not isinstance(preposition_type, PrepositionType):
            raise TypeError("preposition_type must be of type PrepositionType")
        self.name = name
        self.preposition_type = preposition_type

    def __repr__(self) -> str:
        return f"Preposition({self.name}, {self.preposition_type})"

    def __str__(self) -> str:
        return self.name


preposition_dict = {
    "into": Preposition("into", PrepositionType.DIRECTIONAL),
    "onto": Preposition("onto", PrepositionType.DIRECTIONAL),
    "to": Preposition("to", PrepositionType.DIRECTIONAL),
}
