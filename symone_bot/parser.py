"""
Tools to parse queries to the bot.
"""
import collections
import logging
import re
from typing import Generator, List, Pattern, Union

from symone_bot.aspects import Aspect
from symone_bot.commands import Command
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

    def __init__(self, commands: List[Command], aspects: List[Aspect]):
        self.tokens = None
        self.tok = None
        self.nexttok = None
        self.commands = commands
        self.aspects = aspects

    def parse(self, query: str) -> SymoneResponse:
        """
        Parses a query string and returns a SymoneResponse object.
        :param query: query text.
        :return: SymoneResponse object.
        """
        master_pattern = self._get_master_pattern()
        self.tokens = generate_tokens(query, master_pattern)
        self.tok = None  # Last symbol consumed
        self.nexttok = None  # Next symbol tokenized
        self._advance()  # Load first lookahead token
        return self._get_response()

    def _advance(self):
        """Advance one token ahead"""
        self.tok, self.nexttok = self.nexttok, next(self.tokens, None)

    def _accept(self, toktype: str):
        """Test and consume the next token if it matches toktype"""
        if self.nexttok and self.nexttok.type == toktype:
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
        aspect = None
        value = None
        if self.nexttok is None:
            command = self._lookup_command(Token("CMD", "default"))
        else:
            self._expect("CMD")
            cmd_token = self.tok
            command = self._lookup_command(cmd_token)
            if self._accept("ASPECT"):
                aspect_token = self.tok
                aspect = self._lookup_aspect(aspect_token)
                if self._accept("VALUE"):
                    value = self.get_value(self.tok[1])

        logging.info(
            f"Parser: found Command: {command}, Aspect: {aspect}, Value: {value}"
        )
        return SymoneResponse(command, aspect=aspect, value=value)

    @staticmethod
    def get_value(tok: str) -> Union[int, str]:
        if tok.replace(
            "-", ""
        ).isnumeric():  # strip out the negative sign before checking if it's numeric
            return int(tok)
        return tok.replace('"', "")

    def _get_master_pattern(self):
        cmds = ["\\b{}\\b".format(cmd.name) for cmd in self.commands]
        command_match = "|".join(cmds)
        aspects = ["\\b{}\\b".format(cmd.name) for cmd in self.aspects]
        aspect_match = "|".join(aspects)
        cmd = r"(?P<CMD>{})".format(command_match)
        aspect = r"(?P<ASPECT>{})".format(aspect_match)
        val = r'(?P<VALUE>((-|)\d+|"(.*?)"))'
        ws = r"(?P<WS>\s+)"

        pattern = re.compile("|".join([cmd, aspect, val, ws]))
        return pattern

    def _lookup_command(self, cmd_token: Token) -> Command:
        return {cmd.name: cmd for cmd in self.commands}.get(cmd_token[1])

    def _lookup_aspect(self, aspect_token: Token) -> Aspect:
        return {aspect.name: aspect for aspect in self.aspects}.get(aspect_token[1])
