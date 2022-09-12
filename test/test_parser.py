import re

import pytest

from symone_bot.commands import Command
from symone_bot.parser import QueryEvaluator, Token, generate_tokens


@pytest.fixture
def query_evaluator(test_commands, test_aspects):
    return QueryEvaluator(test_commands, test_aspects)


def test_generate_tokens():
    val = r'(?P<VALUE>((-|)\d+|"(.*?)"))'
    ws = r"(?P<WS>\s+)"
    pattern = re.compile("|".join([val, ws]))
    token_generator = generate_tokens('1 2 -3 "rise of the runelords"', pattern)

    token_list = list(token_generator)

    assert len(token_list) == 4
    for token in token_list:
        assert token[0] == "VALUE"

    assert token_list[3][1] == '"rise of the runelords"'


def test_parse(query_evaluator):
    response = query_evaluator.parse("foo bar 3")

    assert response.command.name == "foo"
    assert response.aspect.name == "bar"
    assert response.value == 3


def test_parse_with_negative_number(query_evaluator):
    response = query_evaluator.parse("foo bar -3")

    assert response.command.name == "foo"
    assert response.aspect.name == "bar"
    assert response.value == -3


@pytest.mark.parametrize("query", ["bar foo 3", "3 bar foo", "3 foo", "bar", "3"])
def test_parse_throws_error_if_command_is_not_first(query, query_evaluator):
    with pytest.raises(SyntaxError):
        query_evaluator.parse(query)


def test__get_master_pattern(query_evaluator):
    pattern = query_evaluator._get_master_pattern()

    assert type(pattern) == re.Pattern
    assert pattern == re.compile(
        "(?P<CMD>\\bfoo\\b)|(?P<ASPECT>\\bbar\\b)|(?P<VALUE>((-|)\\d+|\"(.*?)\"))|(?P<WS>\\s+)"
    )


def test__lookup_function(query_evaluator):
    cmd_token = Token("CMD", "foo")
    command = query_evaluator._lookup_command(cmd_token)

    assert command.name == "foo"
    assert command.help_info == "does foo stuff"


def test__lookup_aspect(query_evaluator):
    aspect_token = Token("ASPECT", "bar")
    aspect = query_evaluator._lookup_aspect(aspect_token)

    assert aspect.name == "bar"
    assert aspect.help_info == "a bar aspect"
    assert aspect.value_type == int


@pytest.mark.parametrize(
    "query",
    [
        "tell me something strange?",
        "why did you say that one thing that one time?",
        "I am pickle!",
        "where dog",
        "what is the meaning of life?",
    ],
)
def test__multiline_commands(query, query_evaluator):
    def foo(blank):
        return "foo"

    query = query.replace("?", "")
    query = query.replace("!", "")
    new_command = Command(query, "tells you something strange", foo)

    query_evaluator.commands.append(new_command)

    response = query_evaluator.parse(query)

    assert response.command.name == query
    assert response.command.help_info == "tells you something strange"
    assert response.get() == "foo"
