import typing as ta

from ...errors import AbnfIncompleteParseError
from ...grammars import Grammar
from ...grammars import Rule
from ...matches import Match
from ...matches import longest_match
from ..base import CompiledGrammar
from ..base import Engine
from ..base import EngineCapabilities
from ..base import MatchTreeFidelity
from . import compiled
from . import parsers


##


class InterpCompiledGrammar(CompiledGrammar):
    """
    The default engine: the memoizing, all-matches, true-ABNF interpreter.

    By default op trees are closure-compiled once per grammar (see `compiled`); `no_closures=True` (or any `debug`
    parse) uses the readable reference implementation in `parsers` instead. The two are semantically identical - the
    reference impl is the oracle for the compiled one's differential tests.
    """

    _CAPABILITIES: ta.ClassVar[EngineCapabilities] = EngineCapabilities(
        all_matches=True,
        partial_parses=True,
        any_root=True,
        match_tree=MatchTreeFidelity.OPS,
    )

    def __init__(
            self,
            grammar: Grammar,
            *,
            no_closures: bool = False,
    ) -> None:
        super().__init__()

        self._grammar = grammar

        self._compiled: compiled.CompiledRules | None = None if no_closures else compiled.CompiledRules(grammar)

        self._last_state: compiled.ParseState | None = None  # Debugging aid, inspectable after a parse

    @property
    def grammar(self) -> Grammar:
        return self._grammar

    @property
    def capabilities(self) -> EngineCapabilities:
        return self._CAPABILITIES

    #

    def _match_compiled(
            self,
            cr: compiled.CompiledRules,
            source: str,
            root: Rule | str | None,
            start: int,
            max_steps: int | None,
    ) -> tuple[compiled.ParseState, tuple[Match, ...]]:
        root_rule = self._grammar.resolve_root(root)

        st = compiled.ParseState(source, max_steps=max_steps)
        self._last_state = st

        ms = cr.match_rule(st, root_rule.name_f, start)
        return st, ms

    def _make_reference_parser(
            self,
            source: str,
            *,
            debug: int = 0,
            max_steps: int | None = None,
    ) -> parsers._Parser:  # noqa
        return parsers._make_parser(  # noqa
            self._grammar,
            source,
            debug=debug,
            max_steps=max_steps,
        )

    #

    def iter_parse(
            self,
            source: str,
            root: Rule | str | None = None,
            *,
            start: int = 0,
            debug: int = 0,
            max_steps: int | None = None,
            **kwargs: ta.Any,
    ) -> ta.Iterator[Match]:
        if kwargs:
            raise TypeError(kwargs)

        if (cr := self._compiled) is not None and not debug:
            _, ms = self._match_compiled(cr, source, root, start, max_steps)
            yield from ms
            return

        root_rule = self._grammar.resolve_root(root)

        parser = self._make_reference_parser(source, debug=debug, max_steps=max_steps)

        try:
            yield from parser.iter_parse(
                root_rule._op,  # noqa
                start,
            )
        finally:
            pass  # Debugging aid to inspect parser state after parse

    def parse(
            self,
            source: str,
            root: Rule | str | None = None,
            *,
            start: int = 0,
            complete: bool = False,
            debug: int = 0,
            max_steps: int | None = None,
            **kwargs: ta.Any,
    ) -> Match | None:
        if kwargs:
            raise TypeError(kwargs)

        fo: int | None = None
        tr: ta.Sequence[str] | None = None

        if (cr := self._compiled) is not None and not debug:
            st, ms = self._match_compiled(cr, source, root, start, max_steps)
            match = longest_match(ms)
            if st.furthest_end >= 0:
                fo = st.furthest_end
                tr = st.furthest_trace or None

        else:
            root_rule = self._grammar.resolve_root(root)
            parser = self._make_reference_parser(source, debug=debug, max_steps=max_steps)
            match = longest_match(parser.iter_parse(
                root_rule._op,  # noqa
                start,
            ))
            if (fi := parser.furthest) is not None:
                fo = fi.match.end
                tr = parsers._furthest_rule_trace(fi)  # noqa

        if complete and (match is None or (match.start, match.end) != (start, len(source))):
            raise AbnfIncompleteParseError(
                source=source,
                start=start,
                match_end=match.end if match is not None else None,
                furthest_offset=fo,
                rule_trace=tr,
            )

        return match


class InterpEngine(Engine):
    def __init__(
            self,
            *,
            no_closures: bool = False,
    ) -> None:
        super().__init__()

        self._no_closures = no_closures

    def compile(
            self,
            grammar: Grammar,
            *,
            roots: ta.Iterable[Rule | str] | None = None,
    ) -> CompiledGrammar:
        return InterpCompiledGrammar(
            grammar,
            no_closures=self._no_closures,
        )
