# @omlish-precheck-allow-any-unicode
"""
Lowering of a TokenizedGrammar's parser rules to a context-free grammar over token terminals.

- Terminals are TokenSpecs (named tokens and implicit literals).
- References to skip wrappers (S/R-style whitespace threading) lower to nothing at all - the lexer already handled
  those tokens.
- Each parser rule gets a *rule* nonterminal whose reductions build rule-level Match nodes; all structurally-generated
  nonterminals (alternation branches, repeat spines, options) are *splice* nonterminals whose reductions flatten into
  their parent - keeping emitted trees rule-shaped regardless of lowering details.
- Repeats lower left-recursively (`R -> R x | x`) - constant stack depth per reduction is exactly what LR is good at.
"""
import typing as ta

from ..... import check
from ..... import dataclasses as dc
from ...base import Op
from ...errors import AbnfTokenizationError
from ...internal import Regex
from ...ops import CaseInsensitiveStringLiteral
from ...ops import Concat
from ...ops import Either
from ...ops import RangeLiteral
from ...ops import Repeat
from ...ops import RuleRef
from ...ops import StringLiteral
from ..tokens.specs import SkipKind
from ..tokens.specs import TokenizedGrammar
from ..tokens.specs import TokenSpec


##


@dc.dataclass(frozen=True, eq=False)
class Nt:
    """A nonterminal. Compared by identity - every instance is a distinct symbol."""

    name: str
    is_rule: bool
    """True for a parser rule's own nonterminal: reductions build a rule-level Match node. False for synthetic
    (splice) nonterminals: reductions flatten their children into the parent."""

    rule_name: str
    """The originating parser rule's (original-case) name, for node building and diagnostics."""

    def __repr__(self) -> str:
        return f'Nt({self.name!r})'


Sym: ta.TypeAlias = Nt | TokenSpec


@dc.dataclass(frozen=True, eq=False)
class Production:
    index: int
    lhs: Nt
    rhs: tuple[Sym, ...]

    gaps: frozenset[int] = frozenset()
    """
    Positions where a REQUIRED skip wrapper (R-style, 1*SKIP) was elided: `i in gaps` demands at least one skipped
    (hidden-token) character between rhs[i-1] and rhs[i] - with i == 0 / len(rhs) anchoring to the surrounding context.
    The driver enforces these at reduce time, preserving the char-level grammar's mandatory-whitespace semantics.
    """

    def __repr__(self) -> str:
        return f'{self.lhs.name} -> {" ".join(s.name for s in self.rhs) if self.rhs else "ε"}'


class Cfg:
    def __init__(
            self,
            root_nt: Nt,
            productions: ta.Sequence[Production],
    ) -> None:
        super().__init__()

        self._root_nt = root_nt
        self._productions = list(productions)

        by_lhs: dict[Nt, list[Production]] = {}
        nts: list[Nt] = []
        terminals: dict[int, TokenSpec] = {}
        for p in self._productions:
            if p.lhs not in by_lhs:
                by_lhs[p.lhs] = []
                nts.append(p.lhs)
            by_lhs[p.lhs].append(p)
            for s in p.rhs:
                if isinstance(s, TokenSpec):
                    terminals.setdefault(s.index, s)

        self._by_lhs: ta.Mapping[Nt, ta.Sequence[Production]] = by_lhs
        self._nts: ta.Sequence[Nt] = nts
        self._terminals: ta.Mapping[int, TokenSpec] = terminals

    @property
    def root_nt(self) -> Nt:
        return self._root_nt

    @property
    def productions(self) -> ta.Sequence[Production]:
        return self._productions

    @property
    def by_lhs(self) -> ta.Mapping[Nt, ta.Sequence[Production]]:
        return self._by_lhs

    @property
    def nts(self) -> ta.Sequence[Nt]:
        return self._nts

    @property
    def terminals(self) -> ta.Mapping[int, TokenSpec]:
        return self._terminals

    def render(self) -> str:
        return '\n'.join(repr(p) for p in self._productions)


##


class _Gap:
    """Sentinel emitted where a REQUIRED skip wrapper is elided; stripped into Production.gaps at production build."""

    def __repr__(self) -> str:
        return '<gap>'


_GAP = _Gap()


class CfgLowerer:
    _MAX_BOUNDED_REPEAT = 64

    def __init__(self, tokenized: TokenizedGrammar) -> None:
        super().__init__()

        self._tokenized = tokenized

        self._productions: list[Production] = []
        self._rule_nts: dict[str, Nt] = {}
        self._next_synth: dict[str, int] = {}

        self._cur_rule_name = ''

    def _fresh_nt(self) -> Nt:
        rn = self._cur_rule_name
        i = self._next_synth.get(rn, 0)
        self._next_synth[rn] = i + 1
        return Nt(
            name=f'{rn}.{i}',
            is_rule=False,
            rule_name=rn,
        )

    def _add(self, lhs: Nt, rhs: ta.Sequence[Sym | _Gap]) -> None:
        syms: list[Sym] = []
        gaps: set[int] = set()
        for x in rhs:
            if isinstance(x, _Gap):
                gaps.add(len(syms))
            else:
                syms.append(x)

        self._productions.append(Production(
            index=len(self._productions),
            lhs=lhs,
            rhs=tuple(syms),
            gaps=frozenset(gaps),
        ))

    def _rule_nt(self, name_f: str) -> Nt:
        try:
            return self._rule_nts[name_f]
        except KeyError:
            pass

        r = self._tokenized.parser_rules[name_f]
        nt = self._rule_nts[name_f] = Nt(
            name=r.name,
            is_rule=True,
            rule_name=r.name,
        )
        return nt

    def _lower_op(self, op: Op) -> list[Sym | _Gap]:
        tkz = self._tokenized

        if isinstance(op, RuleRef):
            n = op.name_f
            if (sk := tkz.skip_wrappers.get(n)) is not None:
                return [_GAP] if sk is SkipKind.REQUIRED else []
            if (ts := tkz.token_rule_specs.get(n)) is not None:
                return [ts]
            return [self._rule_nt(n)]

        elif isinstance(op, StringLiteral):
            return [tkz.literal_specs[(op.value, False)]]

        elif isinstance(op, CaseInsensitiveStringLiteral):
            return [tkz.literal_specs[(op.value, True)]]

        elif isinstance(op, RangeLiteral):
            check.state(op.value.lo == op.value.hi)  # enforced at extraction
            return [tkz.literal_specs[(op.value.lo, False)]]

        elif isinstance(op, Concat):
            out: list[Sym | _Gap] = []
            for c in op.children:
                out.extend(self._lower_op(c))
            return out

        elif isinstance(op, Either):
            nt = self._fresh_nt()
            for c in op.children:
                self._add(nt, self._lower_op(c))
            return [nt]

        elif isinstance(op, Repeat):
            body = self._lower_op(op.child)

            t = op.times
            if all(isinstance(x, _Gap) for x in body):
                # an all-skip repeat lowers to nothing - keeping the gap requirement if any repetition is mandatory
                return [_GAP] if (body and t.min >= 1) else []
            if t.max is None:
                spine = self._fresh_nt()
                if t.min == 0:
                    self._add(spine, [])
                    self._add(spine, [spine, *body])
                    return [spine]
                self._add(spine, body)
                self._add(spine, [spine, *body])
                # min >= 2: (min - 1) required copies then the 1+ spine
                return [*(body * (t.min - 1)), spine]

            if t.max > self._MAX_BOUNDED_REPEAT:
                raise AbnfTokenizationError(
                    f'Bounded repeat too large to lower: {t!r}',
                    rule=self._cur_rule_name,
                )

            out2: list[Sym | _Gap] = list(body * t.min)
            if t.max > t.min:
                opt = self._fresh_nt()
                self._add(opt, [])
                self._add(opt, body)
                out2.extend([opt] * (t.max - t.min))
            return out2

        elif isinstance(op, Regex):
            raise AbnfTokenizationError('Regex op in parser rule', rule=self._cur_rule_name)

        else:
            raise TypeError(op)

    def lower(self) -> Cfg:
        tkz = self._tokenized

        root_nt = self._rule_nt(tkz.root.name_f)

        for n, r in tkz.parser_rules.items():
            nt = self._rule_nt(n)
            self._cur_rule_name = r.name
            self._add(nt, self._lower_op(r.op))

        return Cfg(root_nt, self._productions)


def lower_to_cfg(tokenized: TokenizedGrammar) -> Cfg:
    return CfgLowerer(tokenized).lower()
