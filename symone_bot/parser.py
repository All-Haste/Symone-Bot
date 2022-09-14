"""
Tools to parse queries to the bot.
"""
import collections
import logging
import re
from typing import Dict, Generator, Pattern, Union, Tuple

from symone_bot.aspects import Aspect, aspect_dict
from symone_bot.commands import Command, command_dict
from symone_bot.prepositions import Preposition, preposition_dict
from symone_bot.response import SymoneResponse

Token = collections.namedtuple("Token", ["type", "value"])


def generate_tokens(text: str, master_pattern: Pattern) -> Generator:
    """
    Generates tokens (supplied by master_pattern) from the input text.
    :param text: text to tokenize.
    :param master_pattern: regex pattern.
    :return: Generator
    """
    scanner = master_pattern.scanner(text)
    for m in iter(scanner.match, None):
        tok = Token(m.lastgroup, m.group())
        if tok.type != "WS":
            yield tok


class QueryEvaluator:
    """
    A recursive descent parser for parsing through a query with the `parse` method.
    """

    def __init__(
        self,
        commands: Dict[str, Command],
        prepositions: Dict[str, Preposition],
        aspects: Dict[str, Aspect],
    ):
        self.tokens = None
        self.current_token = None
        self.next_token = None
        self.commands = commands
        self.prepositions = prepositions
        self.aspects = aspects

    @staticmethod
    def get_evaluator(
        commands: Dict[str, Command] = None,
        prepositions: Dict[str, Preposition] = preposition_dict,
        aspects: Dict[str, Aspect] = None,
    ):
        """
        Static factory method for creating a QueryEvaluator.
        param commands: List of commands to use.
        param prepositions: Dict of prepositions to use.
        param aspects: List of aspects to use.
        return: QueryEvaluator
        """
        if commands is None:
            commands = command_dict
        if aspects is None:
            aspects = aspect_dict

        return QueryEvaluator(commands, prepositions, aspects)

    def parse(self, query: str) -> SymoneResponse:
        """
        Parses a query string and returns a SymoneResponse object.
        :param query: query text.
        :return: SymoneResponse object.
        """
        master_pattern = self._get_master_pattern()
        self.tokens = generate_tokens(query, master_pattern)
        self.current_token = None  # pragma: no mutate
        self.next_token = None  # pragma: no mutate
        self._advance()  # Load first lookahead token
        return self._get_response()

    def _advance(self):
        """Advance one token ahead"""
        self.current_token, self.next_token = self.next_token, next(self.tokens, None)

    def _accept(self, toktype: str):
        """Test and consume the next token if it matches toktype"""
        if self.next_token and self.next_token.type == toktype:
            self._advance()
            return True
        else:
            return False

    def _expect(self, toktype: str):
        """Consume next token if it matches toktype or raise SyntaxError"""
        if not self._accept(toktype):
            raise SyntaxError("Expected " + toktype)

    def _get_response(self) -> SymoneResponse:
        """Scans through the token set and attempts to return a Command"""
        preposition = None
        aspect = None
        value = None
        if self.next_token is None:
            command = self._lookup_command(Token("CMD", "default"))
        else:
            # the first token must be a command
            self._expect("CMD")
            cmd_token = self.current_token
            command = self._lookup_command(cmd_token)

            if self._accept("ASPECT"):
                aspect, value = self.get_aspect()
            elif self._accept("VALUE") or self._accept("STRING_VALUE"):
                value = self._extract_value_from_token(self.current_token[1])
                if self._accept("PREP"):
                    aspect, preposition = self.get_preposition()

        logging.info(
            f"Parser: found Command: {command}, Aspect: {aspect}, Value: {value}"
        )
        return SymoneResponse(
            command, aspect=aspect, value=value, preposition=preposition
        )

    def get_preposition(self) -> Tuple[Aspect, Preposition]:
        """
        Parses a preposition token and returns it as a Preposition object,
        as well as returning an Aspect and value, since they are required
        """
        preposition_token = self.current_token
        preposition = self._lookup_preposition(preposition_token)
        if self._accept("ASPECT"):
            aspect, _ = self.get_aspect()
        else:
            raise SyntaxError("Expected aspect and value after preposition")
        return aspect, preposition

    def get_aspect(self) -> Tuple[Aspect, Union[str, int]]:
        """
        Parses an aspect token and returns it as an Aspect object,
        as well as returning a value, if it's present.
        """
        value = None
        aspect_token = self.current_token
        aspect = self._lookup_aspect(aspect_token)
        if self._accept("VALUE") or self._accept("STRING_VALUE"):
            value = self._extract_value_from_token(self.current_token[1])
        return aspect, value

    @staticmethod
    def _extract_value_from_token(tok: str) -> Union[int, str]:
        if tok.replace(
            "-", ""
        ).isnumeric():  # strip out the negative sign before checking if it's numeric
            return int(tok)
        return tok.replace('"', "")

    def _get_master_pattern(self):
        cmds = ["\\b{}\\b".format(cmd.name) for cmd in self.commands.values()]
        command_match = "|".join(cmds)
        prepositions = [
            "\\b{}\\b".format(preposition.name)
            for preposition in self.prepositions.values()
        ]
        preposition_match = "|".join(prepositions)
        aspects = ["\\b{}\\b".format(aspect.name) for aspect in self.aspects.values()]
        aspect_match = "|".join(aspects)
        cmd = r"(?P<CMD>{})".format(command_match)
        preposition = r"(?P<PREP>{})".format(preposition_match)
        aspect = r"(?P<ASPECT>{})".format(aspect_match)
        val = r"(?P<VALUE>(-|)\d+)"
        string_val = r'(?P<STRING_VALUE>"(.*?)")'
        ws = r"(?P<WS>\s+)"

        pattern = re.compile(
            "|".join([cmd, aspect, preposition, val, ws, string_val]),
            re.IGNORECASE,
        )
        return pattern

    def _lookup_command(self, cmd_token: Token) -> Command:
        return self.commands.get(cmd_token[1])

    def _lookup_aspect(self, aspect_token: Token) -> Aspect:
        return self.aspects.get(aspect_token[1])

    def _lookup_preposition(self, preposition_token: Token) -> Preposition:
        return self.prepositions.get(preposition_token[1])
