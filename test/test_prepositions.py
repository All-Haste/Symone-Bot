import pytest

from symone_bot.prepositions import Preposition, PrepositionType


def test__preposition_repr():
    assert (
        repr(Preposition("into", PrepositionType.DIRECTIONAL))
        == "Preposition(into, PrepositionType.DIRECTIONAL)"
    )


def test__preposition_str():
    assert str(Preposition("into", PrepositionType.DIRECTIONAL)) == "into"


@pytest.mark.parametrize("invalid_name", [1, 1.0, True, None])
def test__preposition_type_checks_name(invalid_name):
    with pytest.raises(TypeError):
        Preposition(invalid_name, PrepositionType.DIRECTIONAL)


@pytest.mark.parametrize("invalid_preposition_type", [1, 1.0, True, None])
def test__preposition_type_checks_preposition_type(invalid_preposition_type):
    with pytest.raises(TypeError):
        Preposition("foo", invalid_preposition_type)
