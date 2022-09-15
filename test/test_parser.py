import re

import pytest

from symone_bot.commands import Command
from symone_bot.parser import QueryEvaluator, Token, generate_tokens
from symone_bot.prepositions import PrepositionType, preposition_dict


@pytest.fixture
def query_evaluator(test_commands, test_aspects):
    return QueryEvaluator(test_commands, preposition_dict, test_aspects)


def test__evaluator_initial_state(query_evaluator, test_commands, test_aspects):
    assert query_evaluator.tokens is None
    assert query_evaluator.current_token is None
    assert query_evaluator.next_token is None
    assert query_evaluator.commands == test_commands
    assert query_evaluator.prepositions == preposition_dict
    assert query_evaluator.aspects == test_aspects


def test__parse_verify_no_preposition(query_evaluator):
    response = query_evaluator.parse("foo bar 3")

    assert response.command.name == "foo"
    assert response.aspect.name == "bar"
    assert response.value == 3
    assert response.preposition is None


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


@pytest.mark.parametrize(
    "input_string,expected_tokens",
    [
        (
            "foo bar 3",
            [Token("CMD", "foo"), Token("ASPECT", "bar"), Token("VALUE", "3")],
        ),
        (
            "foo bar -3",
            [Token("CMD", "foo"), Token("ASPECT", "bar"), Token("VALUE", "-3")],
        ),
        (
            "foo 1000 to bar",
            [
                Token("CMD", "foo"),
                Token("VALUE", "1000"),
                Token("PREP", "to"),
                Token("ASPECT", "bar"),
            ],
        ),
    ],
)
def test__generate_tokens_with_master_pattern(
    query_evaluator, input_string, expected_tokens
):
    master_pattern = query_evaluator._get_master_pattern()
    tokens = list(generate_tokens(input_string, master_pattern))
    assert tokens == expected_tokens


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


def test__parse_with_preposition(query_evaluator):
    response = query_evaluator.parse(
        "foo 1000 to bar",
    )

    assert response.command.name == "foo"
    assert response.aspect.name == "bar"
    assert response.value == 1000
    assert response.preposition.name == "to"


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


def test__lookup_preposition(query_evaluator):
    prep_token = Token("PREP", "to")
    prep = query_evaluator._lookup_preposition(prep_token)

    assert prep.name == "to"
    assert prep.preposition_type == PrepositionType.DIRECTIONAL


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
    def foo(**kwargs):
        return "foo"

    query = query.replace(
        "?", ""
    )  # todo this needs to be handled in actual application code
    query = query.replace("!", "")
    new_command = Command(query, "tells you something strange", foo)

    query_evaluator.commands[query] = new_command

    response = query_evaluator.parse(query)

    assert response.command.name == query
    assert response.command.help_info == "tells you something strange"
    assert response.get() == "foo"


@pytest.mark.parametrize(
    "command_text,input_value,expected_output",
    [
        ("set the number to", "1000", 1000),
        ("switch campaign to", "Rise of the Runelords", "Rise of the Runelords"),
    ],
)
def test__multiline_no_aspect_modifier_commands(
    command_text, input_value, expected_output, query_evaluator
):
    def foo(value, **kwargs):
        return value

    new_command = Command(command_text, "modifies something", foo)
    new_command.is_modifier = True

    query_evaluator.commands[command_text] = new_command

    if isinstance(expected_output, str):
        input_query = f'{command_text} "{input_value}"'
    else:
        input_query = f"{command_text} {input_value}"
    response = query_evaluator.parse(input_query)

    assert response.command.name == command_text
    assert response.command.help_info == "modifies something"
    assert response.get() == expected_output


@pytest.mark.parametrize(
    "input_string,expected",
    [
        ("3", 3),
        ("-3", -3),
        ('"rise of the runelords"', "rise of the runelords"),
    ],
)
def test__get_value(input_string, expected):
    actual = QueryEvaluator._extract_value_from_token(input_string)
    assert actual == expected


def test__get_preposition(query_evaluator):
    query_evaluator.current_token = Token("PREP", "to")
    query_evaluator.next_token = Token("ASPECT", "bar")
    query_evaluator.tokens = iter(
        [query_evaluator.current_token, query_evaluator.next_token]
    )
    prep, aspect = query_evaluator.get_preposition_then_aspect()

    assert aspect.name == "bar"
    assert prep.name == "to"


def test__get_preposition_raises_syntax_error_if_preposition_not_followed_by_aspect(
    query_evaluator,
):
    query_evaluator.current_token = Token("PREP", "to")
    query_evaluator.tokens = iter([query_evaluator.current_token])
    with pytest.raises(SyntaxError):
        query_evaluator.get_preposition_then_aspect()


def test__get_aspect(query_evaluator):
    query_evaluator.current_token = Token("ASPECT", "bar")
    query_evaluator.next_token = Token("VALUE", "3")
    query_evaluator.tokens = iter(
        [query_evaluator.current_token, query_evaluator.next_token]
    )
    aspect, value, _ = query_evaluator.get_aspect()

    assert aspect.name == "bar"
    assert value == 3


def test__get_aspect_with_no_value(query_evaluator):
    query_evaluator.current_token = Token("ASPECT", "bar")
    query_evaluator.tokens = iter([query_evaluator.current_token])
    aspect, value, _ = query_evaluator.get_aspect()

    assert aspect.name == "bar"
    assert value is None
