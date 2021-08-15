"""
Tools to parse queries to the bot.
"""
import re
import collections

from typing import List, Generator, Pattern

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
    Implementation of a recursive descent parser. Use the ._accept() method
    to test and accept the current lookahead token.  Use the ._expect()
    method to exactly match and discard the next token on the input
    (or raise a SyntaxError if it doesn't match).
    """

    def __init__(self, commands: List[Command], aspects: List[Aspect]):
        self.tokens = None
        self.tok = None
        self.nexttok = None
        self.commands = commands
        self.aspects = aspects

    def parse(self, query) -> SymoneResponse:
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

    def _accept(self, toktype):
        """Test and consume the next token if it matches toktype"""
        if self.nexttok and self.nexttok.type == toktype:
            self._advance()
            return True
        else:
            return False

    def _expect(self, toktype):
        """Consume next token if it matches toktype or raise SyntaxError"""
        if not self._accept(toktype):
            raise SyntaxError("Expected " + toktype)

    def _get_response(self) -> SymoneResponse:
        """Scans through the token set and attempts to return a Command"""
        self._expect("CMD")
        cmd_token = self.tok
        aspect = None
        value = None
        command = self._lookup_command(cmd_token)
        if self._accept("ASPECT"):
            aspect_token = self.tok
            aspect = self._lookup_aspect(aspect_token)
            if self._accept("NUM"):
                value = int(self.tok[1])

        return SymoneResponse(command, aspect=aspect, value=value)

    def _get_master_pattern(self):
        cmds = ["\\b{}\\b".format(cmd.name) for cmd in self.commands]
        command_match = "|".join(cmds)
        aspects = ["\\b{}\\b".format(cmd.name) for cmd in self.aspects]
        aspect_match = "|".join(aspects)
        cmd = r"(?P<CMD>{})".format(command_match)
        aspect = r"(?P<ASPECT>{})".format(aspect_match)
        num = r"(?P<num>\d+)"
        ws = r"(?P<ws>\s+)"

        pattern = re.compile("|".join([cmd, aspect, num, ws]))
        return pattern

    def _lookup_command(self, cmd_token: Token) -> Command:
        return {cmd.name: cmd for cmd in self.commands}.get(cmd_token[1])

    def _lookup_aspect(self, aspect_token: Token) -> Aspect:
        return {aspect.name: aspect for aspect in self.aspects}.get(aspect_token[1])
