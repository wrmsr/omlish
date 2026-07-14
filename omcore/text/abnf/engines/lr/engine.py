"""
The deterministic LALR(1) engine: `compile` lexes-and-lowers the grammar, builds tables (rejecting non-LALR(1)
grammars with a conflict report), and `parse` drives a standard shift/reduce loop over the lexed token stream.

Capability trade-offs vs the interpreter, all declared in `EngineCapabilities`: single parse only (no `iter_parse`),
complete parses only, a single compiled root, and *rule-level* match trees - nodes for parser rules, leaves for named
tokens, nothing for implicit literals - the shape `only_match_rules` produces from interpreter trees.
"""
import typing as ta

from ...errors import AbnfEngineCapabilityError
from ...errors import AbnfUnexpectedTokenError
from ...grammars import Grammar
from ...grammars import Rule
from ...matches import Match
from ...ops import RuleRef
from ...positions import format_offset
from ..base import CompiledGrammar
from ..base import Engine
from ..base import EngineCapabilities
from ..base import MatchTreeFidelity
from ..tokens.extraction import extract_tokenized
from ..tokens.lexing import Lexer
from ..tokens.specs import Token
from ..tokens.specs import TokenSpecKind
from .cfg import lower_to_cfg
from .tables import EOF_TERM
from .tables import LrTables
from .tables import build_tables


##


class LrCompiledGrammar(CompiledGrammar):
    _CAPABILITIES: ta.ClassVar[EngineCapabilities] = EngineCapabilities(
        all_matches=False,
        partial_parses=False,
        any_root=False,
        match_tree=MatchTreeFidelity.RULES,
    )

    def __init__(
            self,
            grammar: Grammar,
            root: Rule,
            lexer: Lexer,
            tables: LrTables,
    ) -> None:
        super().__init__()

        self._grammar = grammar
        self._root = root
        self._lexer = lexer
        self._tables = tables

        # Canonical per-name RuleRef ops for emitted Match nodes - consumers key off RuleRef.name.
        self._rule_refs: dict[str, RuleRef] = {}

    @property
    def grammar(self) -> Grammar:
        return self._grammar

    @property
    def capabilities(self) -> EngineCapabilities:
        return self._CAPABILITIES

    @property
    def lexer(self) -> Lexer:
        return self._lexer

    @property
    def tables(self) -> LrTables:
        return self._tables

    def lex(self, source: str, *, start: int = 0) -> list[Token]:
        """The full token stream, hidden (space/comment channel) tokens included."""

        return self._lexer.lex(source, start=start)

    #

    def _rule_ref(self, name: str) -> RuleRef:
        try:
            return self._rule_refs[name]
        except KeyError:
            pass
        rr = self._rule_refs[name] = RuleRef(name)
        return rr

    def _check_root(self, root: Rule | str | None) -> None:
        if root is None:
            return
        rn = (root.name_f if isinstance(root, Rule) else root.casefold())
        if rn != self._root.name_f:
            raise AbnfEngineCapabilityError(
                f'LR engine compiled for root {self._root.name!r} cannot parse from {rn!r} - compile a separate '
                f'grammar for that root',
            )

    def iter_parse(
            self,
            source: str,
            root: Rule | str | None = None,
            *,
            start: int = 0,
            **kwargs: ta.Any,
    ) -> ta.Iterator[Match]:
        raise AbnfEngineCapabilityError(
            'The LR engine produces a single deterministic parse - use parse(), or the interpreter engine for '
            'iter_parse',
        )

    def parse(
            self,
            source: str,
            root: Rule | str | None = None,
            *,
            start: int = 0,
            complete: bool = False,
            **kwargs: ta.Any,
    ) -> Match | None:
        if kwargs:
            raise TypeError(kwargs)
        self._check_root(root)
        if not complete:
            raise AbnfEngineCapabilityError(
                'The LR engine only supports complete parses - pass complete=True',
            )

        toks = [t for t in self._lexer.lex(source, start=start) if not t.spec.hidden]
        return self._drive(source, toks, start)

    def _drive(self, source: str, toks: ta.Sequence[Token], start: int) -> Match:
        tables = self._tables
        cfg = tables.cfg
        action = tables.action
        goto = tables.goto
        rule_ref = self._rule_ref

        states = [0]
        # Per stack symbol: (span start, span end, rule-level match nodes)
        vals: list[tuple[int, int, list[Match]]] = []

        i = 0
        n = len(toks)
        last_end = start  # end of consumed input; empty reductions anchor here, not at the next token

        while True:
            st = states[-1]

            if i < n:
                tok = toks[i]
                tkey = tok.spec.index
            else:
                tok = None
                tkey = EOF_TERM

            a = action[st].get(tkey)

            if a is None:
                pos = tok.start if tok is not None else len(source)
                raise AbnfUnexpectedTokenError(
                    source=source,
                    offset=pos,
                    got=f'{tok.spec.name} {tok.text(source)!r}' if tok is not None else None,
                    expected=[
                        '<eof>' if t == EOF_TERM else cfg.terminals[t].name
                        for t in tables.expected_terms(st)
                    ],
                )

            op = a[0]

            if op == 's':
                stok = toks[i]  # a shift action can never be taken at EOF
                states.append(a[1])
                if stok.spec.kind is TokenSpecKind.RULE:
                    ms = [Match(rule_ref(stok.spec.name), stok.start, stok.end, ())]
                else:
                    ms = []
                vals.append((stok.start, stok.end, ms))
                last_end = stok.end
                i += 1

            elif op == 'r':
                prod = cfg.productions[a[1]]
                k = len(prod.rhs)

                if k:
                    popped = vals[-k:]
                    del vals[-k:]
                    del states[-k:]
                    children = [m for e in popped for m in e[2]]
                    # Span is the hull of real content only - zero-width (all-empty) entries sit at bookkeeping
                    # positions and must not stretch enclosing spans across skipped input.
                    lo: int | None = None
                    hi = 0
                    for s_, e_, _ in popped:
                        if e_ > s_:
                            if lo is None:
                                lo = s_
                            hi = e_
                    span = (lo, hi) if lo is not None else (last_end, last_end)
                else:
                    popped = []
                    span = (last_end, last_end)
                    children = []

                if prod.gaps:
                    self._check_gaps(source, toks, i, start, vals, popped, prod)

                if prod.lhs.is_rule:
                    ms = [Match(rule_ref(prod.lhs.rule_name), span[0], span[1], tuple(children))]
                else:
                    ms = children

                states.append(goto[states[-1]][prod.lhs])
                vals.append((span[0], span[1], ms))

            else:  # accept
                (_, _, ms) = vals[-1]
                [m] = ms
                return m

    def _check_gaps(
            self,
            source: str,
            toks: ta.Sequence[Token],
            ti: int,
            start: int,
            vals: ta.Sequence[tuple[int, int, list[Match]]],
            popped: ta.Sequence[tuple[int, int, list[Match]]],
            prod: ta.Any,
    ) -> None:
        """
        Enforces the production's required-skip (elided R) boundaries: at least one skipped character must separate
        the nearest real content on either side. Zero-width (all-epsilon) entries are transparent - the requirement
        looks through them to surrounding tokens, the stack below, the lookahead, or the parse bounds.
        """

        k = len(prod.rhs)

        for gi in sorted(prod.gaps):
            left = start
            for j in range(gi - 1, -1, -1):
                s, e, _ = popped[j]
                if e > s:
                    left = e
                    break
            else:
                for j in range(len(vals) - 1, -1, -1):
                    s, e, _ = vals[j]
                    if e > s:
                        left = e
                        break

            right = len(source)
            for j in range(gi, k):
                s, e, _ = popped[j]
                if e > s:
                    right = s
                    break
            else:
                if ti < len(toks):
                    right = toks[ti].start

            if not left < right:
                raise AbnfUnexpectedTokenError(
                    msg=(
                        f'Required whitespace/skip missing at offset {right}'
                        f'{f" ({format_offset(source, right)})" if right <= len(source) else ""}'
                        f' (rule {prod.lhs.rule_name!r})'
                    ),
                    source=source,
                    offset=right,
                )


class LrEngine(Engine):
    def __init__(
            self,
            *,
            no_adjacency_check: bool = False,
    ) -> None:
        super().__init__()

        self._no_adjacency_check = no_adjacency_check

    def compile(
            self,
            grammar: Grammar,
            *,
            roots: ta.Iterable[Rule | str] | None = None,
    ) -> CompiledGrammar:
        root: Rule | str | None = None
        if roots is not None:
            rl = list(roots)
            if len(rl) != 1:
                raise AbnfEngineCapabilityError('The LR engine compiles for exactly one root')
            root = rl[0]

        tkz = extract_tokenized(
            grammar,
            root,
            no_adjacency_check=self._no_adjacency_check,
        )

        lexer = Lexer(tkz)
        cfg = lower_to_cfg(tkz)
        tables = build_tables(cfg)

        return LrCompiledGrammar(
            grammar,
            tkz.root,
            lexer,
            tables,
        )
