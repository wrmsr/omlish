"""
Maximal-munch lexer over a TokenizedGrammar's token set.

At each position every candidate token is tried and the longest match wins; equal lengths tie-break by spec priority
(implicit literals first - keywords beat identifier-shaped tokens - then token rules in declaration order).

Each token rule matches via one of two paths:

- **regex fast path**: the rule's inlined op converts to a single compiled pattern when that is provably
  longest-match-preserving (prefix-free shapes, or trailing repeats of fixed-length pieces - greedy quantifier counts
  are maximal, so more iterations is always a longer match);
- **interp fallback**: correct for *any* token rule - the closure-compiled interpreter matches the rule and the
  longest result is taken. One ParseState is shared per lex run, so memoization amortizes across positions.

A first-char dispatch table (from the tokens' FIRST sets) skips tokens that provably cannot start at the current char.
"""
import re
import typing as ta

from ..... import check
from ...base import Op
from ...errors import AbnfLexError
from ...grammars import Grammar
from ...grammars import Rule
from ...ops import Concat
from ...ops import Repeat
from ...opto import _first_chars  # noqa
from ...opto import _is_prefix_free  # noqa
from ...opto import _len_bounds  # noqa
from ...opto import _regex_item_transform_op  # noqa
from ...opto import _RegexItem  # noqa
from ..interp import compiled as interp_compiled
from .specs import Token
from .specs import TokenizedGrammar
from .specs import TokenSpec
from .specs import TokenSpecKind


##


def _is_fixed_len(op: Op) -> bool:
    mn, mx = _len_bounds(op)
    return mx is not None and mn == mx


def _is_token_longest_safe(op: Op) -> bool:
    """
    True if a greedy regex compiled from `op` provably yields the *longest* match at any position - the semantics
    maximal-munch lexing requires. Conservative: False means 'use the interp fallback', never 'wrong answer'.
    """

    if _is_prefix_free(op):
        return True  # unique match end - nothing to get wrong

    if isinstance(op, Repeat):
        # Greedy iteration count is maximal, and fixed-length iterations make length monotone in count.
        return _is_fixed_len(op.child)

    if isinstance(op, Concat):
        *head, last = op.children
        return all(_is_fixed_len(c) for c in head) and _is_token_longest_safe(last)

    return False


##


class _LexRun:
    """Per-lex mutable state: the shared interp ParseState is created lazily on first fallback-token attempt."""

    def __init__(self, source: str) -> None:
        super().__init__()

        self.source = source
        self.interp_state: interp_compiled.ParseState | None = None


class _Matcher(ta.Protocol):
    def __call__(self, run: _LexRun, pos: int) -> int: ...  # returns match end, or -1


def _make_literal_matcher(spec: TokenSpec) -> _Matcher:
    value = spec.literal_value or ''
    n = len(value)

    if not spec.literal_case_insensitive:
        def m(run: _LexRun, pos: int) -> int:
            if run.source.startswith(value, pos):
                return pos + n
            return -1

        return m

    fvalue = value.casefold()
    fn = len(fvalue)

    def cim(run: _LexRun, pos: int) -> int:
        source = run.source

        s = source[pos:pos + fn]
        folded = s.casefold()
        if len(folded) == fn and len(s) == fn:
            return pos + fn if folded == fvalue else -1

        end = pos
        folded = ''
        while len(folded) < fn:
            if end >= len(source):
                return -1
            folded += source[end].casefold()
            end += 1
        return end if folded == fvalue else -1

    return cim


def _make_regex_matcher(pat: re.Pattern) -> _Matcher:
    pat_match = pat.match

    def m(run: _LexRun, pos: int) -> int:
        if (mo := pat_match(run.source, pos)) is not None:
            return mo.end()
        return -1

    return m


def _make_interp_matcher(cr: interp_compiled.CompiledRules, name_f: str) -> _Matcher:
    def m(run: _LexRun, pos: int) -> int:
        if (st := run.interp_state) is None:
            st = run.interp_state = interp_compiled.ParseState(run.source)
        best = -1
        for tm in cr.match_rule(st, name_f, pos):
            if tm.end > best:
                best = tm.end
        return best

    return m


##


class Lexer:
    def __init__(
            self,
            tokenized: TokenizedGrammar,
    ) -> None:
        super().__init__()

        self._tokenized = tokenized

        self._matchers: list[tuple[TokenSpec, _Matcher]] = []
        self._compile_matchers()
        self._dispatch, self._always = self._build_dispatch()

    _DISPATCH_MAX_CHARS: ta.ClassVar[int] = 512

    def _compile_matchers(self) -> None:
        tkz = self._tokenized

        # Token rules that can't take the regex path share one synthetic grammar of their (validated ref-free) inlined
        # ops, compiled once via the interp engine.
        regexes: dict[str, re.Pattern] = {}
        fallback_names: list[str] = []

        for name_f, iop in tkz.token_rule_ops.items():
            if (
                    _is_token_longest_safe(iop) and
                    (ri := _regex_item_transform_op(iop) or _RegexItem.of_op(iop)) is not None
            ):
                regexes[name_f] = re.compile(ri.pat)
            else:
                fallback_names.append(name_f)

        fallback_cr = self._build_fallback_rules(fallback_names) if fallback_names else None

        for spec in tkz.specs:
            if spec.kind is TokenSpecKind.LITERAL:
                self._matchers.append((spec, _make_literal_matcher(spec)))
                continue

            name_f = spec.name.casefold()
            if (pat := regexes.get(name_f)) is not None:
                self._matchers.append((spec, _make_regex_matcher(pat)))
            else:
                self._matchers.append((spec, _make_interp_matcher(check.not_none(fallback_cr), name_f)))

    def _build_fallback_rules(self, names_f: ta.Sequence[str]) -> interp_compiled.CompiledRules:
        # Inlined ops are self-contained, so the synthetic grammar needs no other rules.
        rules = [
            Rule(n, self._tokenized.token_rule_ops[n])
            for n in names_f
        ]
        return interp_compiled.CompiledRules(Grammar(*rules))

    def _build_dispatch(self) -> tuple[dict[str, tuple[tuple[TokenSpec, _Matcher], ...]], tuple[tuple[TokenSpec, _Matcher], ...]]:  # noqa
        infos: list[tuple[ta.Any, tuple[TokenSpec, _Matcher]]] = []  # (first-chars | None, entry)

        for spec, m in self._matchers:
            if spec.kind is TokenSpecKind.LITERAL:
                v = (spec.literal_value or '')[0]
                if spec.literal_case_insensitive:
                    fcs: set[str] = {c for x in (v, v.lower(), v.upper(), v.casefold()) if len(x) == 1 for c in x}
                else:
                    fcs = {v}
                infos.append((fcs, (spec, m)))
            else:
                iop = self._tokenized.token_rule_ops[spec.name.casefold()]
                ivs = _first_chars(iop)
                if ivs is None or sum(ord(hi) - ord(lo) + 1 for lo, hi in ivs) > self._DISPATCH_MAX_CHARS:
                    infos.append((None, (spec, m)))
                else:
                    fcs = {chr(cp) for lo, hi in ivs for cp in range(ord(lo), ord(hi) + 1)}
                    infos.append((fcs, (spec, m)))

        all_chars: set[str] = set()
        for fcs, _ in infos:
            if fcs is not None:
                all_chars |= fcs

        dispatch = {
            ch: tuple(e for fcs, e in infos if fcs is None or ch in fcs)
            for ch in all_chars
        }
        always = tuple(e for fcs, e in infos if fcs is None)
        return (dispatch, always)

    #

    @property
    def tokenized(self) -> TokenizedGrammar:
        return self._tokenized

    def lex(
            self,
            source: str,
            *,
            start: int = 0,
    ) -> list[Token]:
        run = _LexRun(source)
        dispatch = self._dispatch
        always = self._always

        out: list[Token] = []
        pos = start
        n = len(source)

        while pos < n:
            entries = dispatch.get(source[pos], always)

            best_end = -1
            best_spec: TokenSpec | None = None
            for spec, m in entries:
                end = m(run, pos)
                if end > best_end:
                    best_end = end
                    best_spec = spec

            if best_spec is None or best_end <= pos:
                raise AbnfLexError(source=source, offset=pos)

            out.append(Token(best_spec, pos, best_end))
            pos = best_end

        return out
