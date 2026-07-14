"""
The engine seam: an `Engine` compiles a `Grammar` into a `CompiledGrammar` - the expensive, cacheable step - and a
`CompiledGrammar` parses source texts - the cheap, per-call step.

Engines differ in which parses they produce and what they demand of grammars, never in the shape of the `Match` trees
they emit (though they may differ in *fidelity* - full op-level trees vs rule-level-only trees). Those differences are
data, not documentation: each `CompiledGrammar` reports an `EngineCapabilities`, and requesting an unsupported
capability raises `AbnfEngineCapabilityError` loudly rather than silently degrading.
"""
import abc
import enum
import typing as ta

from .... import dataclasses as dc
from .... import lang
from ..grammars import Grammar
from ..grammars import Rule
from ..matches import Match


##


class MatchTreeFidelity(enum.Enum):
    OPS = enum.auto()  # full op-level trees: every Concat / Repeat / Either / literal node present
    RULES = enum.auto()  # rule-level nodes only, as if filtered through only_match_rules


@dc.dataclass(frozen=True, kw_only=True)
class EngineCapabilities:
    all_matches: bool = False
    """iter_parse is supported and yields every possible match."""

    partial_parses: bool = False
    """Matches not spanning to the end of the source are supported (parse(complete=False))."""

    any_root: bool = False
    """Any rule may be used as a parse root without recompiling."""

    match_tree: MatchTreeFidelity = MatchTreeFidelity.OPS


##


class CompiledGrammar(lang.Abstract):
    @property
    @abc.abstractmethod
    def grammar(self) -> Grammar:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def capabilities(self) -> EngineCapabilities:
        raise NotImplementedError

    @abc.abstractmethod
    def iter_parse(
            self,
            source: str,
            root: Rule | str | None = None,
            *,
            start: int = 0,
            **kwargs: ta.Any,
    ) -> ta.Iterator[Match]:
        raise NotImplementedError

    @abc.abstractmethod
    def parse(
            self,
            source: str,
            root: Rule | str | None = None,
            *,
            start: int = 0,
            complete: bool = False,
            **kwargs: ta.Any,
    ) -> Match | None:
        raise NotImplementedError


class Engine(lang.Abstract):
    @abc.abstractmethod
    def compile(
            self,
            grammar: Grammar,
            *,
            roots: ta.Iterable[Rule | str] | None = None,
    ) -> CompiledGrammar:
        raise NotImplementedError
