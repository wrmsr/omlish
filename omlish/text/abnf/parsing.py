"""
Top-level parsing facade: routes through the default (interpreter) engine, compiling grammars on first use and caching
the compiled artifact per grammar instance.
"""
import typing as ta
import weakref

from ... import check
from .base import Op
from .engines.base import CompiledGrammar
from .engines.base import Engine
from .engines.interp import InterpEngine
from .grammars import Grammar
from .grammars import Rule
from .matches import Match
from .matches import longest_match


##


class _EngineCache:
    def __init__(self, engine: Engine) -> None:
        super().__init__()

        self._engine = engine
        self._compiled: ta.MutableMapping[Grammar, CompiledGrammar] = weakref.WeakKeyDictionary()

    def compile(self, grammar: Grammar) -> CompiledGrammar:
        # Benign race: compilation is pure, so concurrent compiles of the same grammar just waste a little work.
        try:
            return self._compiled[grammar]
        except KeyError:
            pass
        cg = self._compiled[grammar] = self._engine.compile(grammar)
        return cg


_DEFAULT_ENGINE_CACHE = _EngineCache(InterpEngine())


def _default_compiled(grammar: Grammar) -> CompiledGrammar:
    return _DEFAULT_ENGINE_CACHE.compile(grammar)


##


def iter_parse(
        obj: Grammar | Rule | Op,
        src: str,
        *,
        root: str | None = None,
        start: int = 0,
        debug: int = 0,
        max_steps: int | None = None,
) -> ta.Iterator[Match]:
    if isinstance(obj, Grammar):
        gram = obj
    elif isinstance(obj, Rule):
        check.none(root)
        gram = Grammar(obj, root=obj)
    elif isinstance(obj, Op):
        check.none(root)
        gram = Grammar(Rule('root', obj), root='root')
    else:
        raise TypeError(obj)

    return gram.iter_parse(
        src,
        root,
        start=start,
        debug=debug,
        max_steps=max_steps,
    )


def parse(
        obj: Grammar | Rule | Op,
        src: str,
        *,
        root: str | None = None,
        start: int = 0,
        debug: int = 0,
        max_steps: int | None = None,
) -> Match | None:
    return longest_match(iter_parse(
        obj,
        src,
        root=root,
        start=start,
        debug=debug,
        max_steps=max_steps,
    ))
