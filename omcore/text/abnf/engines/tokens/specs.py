import enum
import typing as ta

from ..... import dataclasses as dc
from ...base import Op
from ...grammars import Channel
from ...grammars import Grammar
from ...grammars import Rule


##


class TokenSpecKind(enum.Enum):
    RULE = enum.auto()  # a %token rule
    LITERAL = enum.auto()  # an implicit token synthesized from a literal in a parser rule


@dc.dataclass(frozen=True, kw_only=True)
class TokenSpec:
    index: int
    """Position in the token set - doubles as maximal-munch tie-break priority (lower wins)."""

    name: str
    """The rule name for RULE specs; a repr-ish display name like '"select"' for LITERAL specs."""

    kind: TokenSpecKind

    channel: Channel = Channel.STRUCTURE

    literal_value: str | None = None
    literal_case_insensitive: bool = False

    @property
    def hidden(self) -> bool:
        """Hidden tokens are lexed and retained in the token stream but not fed to a parser."""

        return self.channel in (Channel.SPACE, Channel.COMMENT)


@dc.dataclass(frozen=True)
class Token:
    spec: TokenSpec
    start: int
    end: int

    def text(self, source: str) -> str:
        return source[self.start:self.end]


class SkipKind(enum.Enum):
    OPTIONAL = enum.auto()  # nullable - 'S'-like, zero or more skip tokens
    REQUIRED = enum.auto()  # non-nullable - 'R'-like, one or more skip tokens


@dc.dataclass(frozen=True, kw_only=True)
class TokenizedGrammar:
    """
    A grammar's token-level interpretation: which rules are lexed tokens (explicit and implicit), which parser rules
    are 'skip wrappers' to be elided (whitespace/comment threading like S/R), and the validated parser rules remaining.
    """

    grammar: Grammar
    root: Rule

    specs: ta.Sequence[TokenSpec]

    token_rule_specs: ta.Mapping[str, TokenSpec]  # keyed by casefolded rule name
    token_rule_ops: ta.Mapping[str, Op]  # casefolded rule name -> fully-inlined (ref-free) op
    literal_specs: ta.Mapping[tuple[str, bool], TokenSpec]  # keyed by (value, case_insensitive)

    skip_wrappers: ta.Mapping[str, SkipKind]  # casefolded rule name -> kind

    parser_rules: ta.Mapping[str, Rule]  # casefolded rule name -> rule, reachable from root, validated
