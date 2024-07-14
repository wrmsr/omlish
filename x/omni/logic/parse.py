import re
import typing as ta

from .. import check
from .interpret import Compound
from .interpret import Conjunction
from .interpret import Rule
from .interpret import Term
from .interpret import Truth
from .interpret import Variable


TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|:\-|[()\.,]")
ATOM_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_]+$")
VARIABLE_PATTERN = re.compile(r"^[A-Z_][A-Za-z0-9_]*$")
COMMENT_PATTERN = re.compile(r"(\".*?\"|\'.*?\')|(/\*.*?\*/|%[^\r\n]*$)", re.MULTILINE | re.DOTALL)


def remove_comments(input_text: str) -> str:
    def remove_comment(match):
        if match.group(2) is not None:
            return ''
        else:
            return match.group(1)

    return COMMENT_PATTERN.sub(remove_comment, input_text)


def parse_tokens_from_string(input_text: str) -> ta.List[str]:
    iterator = TOKEN_PATTERN.finditer(remove_comments(input_text))
    return [token.group() for token in iterator]


class Parser:

    def __init__(self, input_text: str) -> None:
        super().__init__()

        self._tokens = parse_tokens_from_string(input_text)
        self._scope: ta.Optional[ta.Dict[str, Term]] = None

    def parse_rules(self) -> ta.Sequence[Rule]:
        rules = []
        while self._tokens:
            self._scope = {}
            rules.append(self._parse_rule())
        return rules

    def parse_query(self) -> Compound:
        self._scope = {}
        return check.isinstance(self._parse_term(), Compound)

    @property
    def _current(self) -> str:
        return self._tokens[0]

    def _pop_current(self) -> str:
        return self._tokens.pop(0)

    def _parse_atom(self) -> str:
        name = self._pop_current()
        if ATOM_NAME_PATTERN.match(name) is None:
            raise Exception('Invalid Atom Name: ' + str(name))
        return name

    def _parse_term(self) -> Term:
        if self._current == '(':
            self._pop_current()
            arguments = self._parse_arguments()
            return Conjunction(arguments)

        functor = self._parse_atom()

        if VARIABLE_PATTERN.match(functor) is not None:
            if functor == '_':
                return Variable('_')

            scope = check.not_none(self._scope)
            variable = scope.get(functor)

            if variable is None:
                scope[functor] = Variable(functor)
                variable = scope[functor]

            return variable

        if self._current != '(':
            return Compound(functor)

        self._pop_current()
        arguments = self._parse_arguments()
        return Compound(functor, arguments)

    def _parse_arguments(self) -> ta.List[Term]:
        arguments = []
        while self._current != ')':
            arguments.append(self._parse_term())
            if self._current not in (',', ')'):
                raise Exception('Expected , or ) in term but got ' + str(self._current))
            if self._current == ',':
                self._pop_current()
        self._pop_current()
        return arguments

    def _parse_rule(self) -> Rule:
        head = self._parse_term()

        if self._current == '.':
            self._pop_current()
            return Rule(head, Truth())

        if self._current != ':-':
            raise Exception('Expected :- in rule but got ' + str(self._current))

        self._pop_current()

        arguments = []

        while self._current != '.':
            arguments.append(self._parse_term())

            if self._current not in (',', '.'):
                raise Exception('Expected , or . in term but got ' + str(self._current))

            if self._current == ',':
                self._pop_current()

        self._pop_current()

        tail = arguments[0] if arguments == 1 else Conjunction(arguments)
        return Rule(head, tail)
