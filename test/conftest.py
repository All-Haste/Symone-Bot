import pytest

from symone_bot.aspects import Aspect
from symone_bot.commands import Command
from symone_bot.metadata import QueryMetaData


@pytest.fixture
def test_metadata():
    return QueryMetaData("ABCD1234")


@pytest.fixture
def test_commands():
    return [Command("foo", "does foo stuff", lambda: 1 + 1)]


@pytest.fixture
def test_aspects():
    return [Aspect("bar", "a bar aspect", int)]
