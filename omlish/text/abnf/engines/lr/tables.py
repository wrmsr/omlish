# @omlish-precheck-allow-any-unicode
"""
LALR(1) parse-table construction: LR(0) automaton plus DeRemer-Pennello lookahead computation (DR / reads / includes /
lookback, closed with the digraph algorithm).

Grammars that are not LALR(1) are rejected at construction with an `AbnfLrConflictError` carrying a per-conflict
report: the state's item set, the lookahead token, and the competing actions - the compile-time contract this engine
trades the interpreter's nondeterminism away for.

Terminal keys are `TokenSpec.index` ints, with `EOF_TERM` (-1) for end-of-input. Actions are small tuples:
`('s', state)`, `('r', production_index)`, `('acc',)`.
"""
import math
import typing as ta

from ...errors import AbnfLrConflictError
from ..tokens.specs import TokenSpec
from .cfg import Cfg
from .cfg import Nt
from .cfg import Production
from .cfg import Sym


Action: ta.TypeAlias = tuple  # ('s', int) | ('r', int) | ('acc',)

_Item: ta.TypeAlias = tuple[Production, int]  # (production, dot)


EOF_TERM = -1


##


def _sym_key(s: Sym) -> tuple:
    if isinstance(s, TokenSpec):
        return (0, s.index)
    return (1, s.name)


def _render_item(it: _Item) -> str:
    prod, dot = it
    parts = [s.name for s in prod.rhs]
    parts.insert(dot, '•')
    return f'{prod.lhs.name} -> {" ".join(parts)}'


def _digraph(
        nodes: ta.Sequence[ta.Any],
        edges: ta.Callable[[ta.Any], ta.Sequence[ta.Any]],
        base: ta.Callable[[ta.Any], ta.AbstractSet[int]],
) -> dict[ta.Any, set[int]]:
    """DeRemer-Pennello relation closure: F(x) = base(x) U union{F(y) : x R y}, with SCC members sharing one set."""

    n: dict[ta.Any, float] = dict.fromkeys(nodes, 0)
    f: dict[ta.Any, set[int]] = {}
    stack: list = []

    def traverse(x0: ta.Any) -> None:
        # Explicit-stack DFS so deep grammars can't hit the recursion limit.
        frames: list[list] = []

        def enter(v: ta.Any) -> None:
            stack.append(v)
            n[v] = len(stack)
            f[v] = set(base(v))
            frames.append([v, len(stack), iter(edges(v))])

        enter(x0)
        while frames:
            v, d, it = frames[-1]

            child = None
            for y in it:
                if n[y] == 0:
                    child = y
                    break
                n[v] = min(n[v], n[y])
                f[v] |= f[y]
            if child is not None:
                enter(child)
                continue

            frames.pop()

            if n[v] == d:
                while True:
                    top = stack.pop()
                    n[top] = math.inf
                    f[top] = f[v]
                    if top == v:
                        break

            if frames:
                pv = frames[-1][0]
                n[pv] = min(n[pv], n[v])
                f[pv] |= f[v]

    for x in nodes:
        if n[x] == 0:
            traverse(x)

    return f


##


class LrTables:
    def __init__(
            self,
            cfg: Cfg,
            *,
            closures: ta.Sequence[frozenset[_Item]],
            action: ta.Sequence[ta.Mapping[int, Action]],
            goto: ta.Sequence[ta.Mapping[Nt, int]],
    ) -> None:
        super().__init__()

        self._cfg = cfg
        self._closures = closures
        self._action = action
        self._goto = goto

    @property
    def cfg(self) -> Cfg:
        return self._cfg

    @property
    def num_states(self) -> int:
        return len(self._closures)

    @property
    def action(self) -> ta.Sequence[ta.Mapping[int, Action]]:
        return self._action

    @property
    def goto(self) -> ta.Sequence[ta.Mapping[Nt, int]]:
        return self._goto

    def expected_terms(self, state: int) -> list[int]:
        return sorted(self._action[state])

    def render_state(self, state: int) -> str:
        return '\n'.join(
            _render_item(it)
            for it in sorted(self._closures[state], key=lambda it: (it[0].index, it[1]))
        )


##


class LrTableBuilder:
    def __init__(self, cfg: Cfg) -> None:
        super().__init__()

        self._cfg = cfg

        self._aug = Production(index=-1, lhs=Nt(name="$'", is_rule=False, rule_name="$'"), rhs=(cfg.root_nt,))

    # LR(0) automaton

    def _closure(self, kernel: frozenset[_Item]) -> frozenset[_Item]:
        out: set[_Item] = set(kernel)
        stack: list[_Item] = list(kernel)
        while stack:
            prod, dot = stack.pop()
            if dot >= len(prod.rhs):
                continue
            s = prod.rhs[dot]
            if isinstance(s, Nt):
                for p in self._cfg.by_lhs.get(s, ()):
                    it = (p, 0)
                    if it not in out:
                        out.add(it)
                        stack.append(it)
        return frozenset(out)

    def _build_automaton(self) -> None:
        self._kernels: list[frozenset[_Item]] = [frozenset([(self._aug, 0)])]
        self._closures: list[frozenset[_Item]] = []
        self._term_goto: list[dict[int, int]] = []
        self._nt_goto: list[dict[Nt, int]] = []

        index_by_kernel: dict[frozenset[_Item], int] = {self._kernels[0]: 0}

        i = 0
        while i < len(self._kernels):
            clo = self._closure(self._kernels[i])
            self._closures.append(clo)

            by_sym: dict[Sym, list[_Item]] = {}
            for prod, dot in clo:
                if dot < len(prod.rhs):
                    by_sym.setdefault(prod.rhs[dot], []).append((prod, dot))

            tg: dict[int, int] = {}
            ng: dict[Nt, int] = {}
            for s in sorted(by_sym, key=_sym_key):  # deterministic state numbering
                nk = frozenset((p, d + 1) for p, d in by_sym[s])
                if (ni := index_by_kernel.get(nk)) is None:
                    ni = len(self._kernels)
                    index_by_kernel[nk] = ni
                    self._kernels.append(nk)
                if isinstance(s, TokenSpec):
                    tg[s.index] = ni
                else:
                    ng[s] = ni

            self._term_goto.append(tg)
            self._nt_goto.append(ng)
            i += 1

    def _goto_state(self, state: int, s: Sym) -> int:
        if isinstance(s, TokenSpec):
            return self._term_goto[state][s.index]
        return self._nt_goto[state][s]

    # nullability / lookaheads

    def _solve_nullable(self) -> None:
        nullable: set[Nt] = set()
        changed = True
        while changed:
            changed = False
            for p in self._cfg.productions:
                if p.lhs in nullable:
                    continue
                if all(isinstance(s, Nt) and s in nullable for s in p.rhs):
                    nullable.add(p.lhs)
                    changed = True
        self._nullable = nullable

    def _solve_lookaheads(self) -> None:
        nt_trans: list[tuple[int, Nt]] = [
            (si, nt)
            for si, ng in enumerate(self._nt_goto)
            for nt in ng
        ]

        # DR(p, A) = terminals shiftable from goto(p, A); EOF follows the root at the start state
        def dr(x: tuple[int, Nt]) -> set[int]:
            p, a = x
            r = self._nt_goto[p][a]
            out = set(self._term_goto[r])
            if a is self._cfg.root_nt and p == 0:
                out.add(EOF_TERM)
            return out

        # reads: (p, A) -> (r, C) where goto(p, A) has an Nt transition on nullable C
        def reads(x: tuple[int, Nt]) -> list[tuple[int, Nt]]:
            p, a = x
            r = self._nt_goto[p][a]
            return [(r, c) for c in self._nt_goto[r] if c in self._nullable]

        read_f = _digraph(nt_trans, reads, dr)

        # includes: (q, A) includes (p, B) iff B -> beta A gamma with gamma nullable and p -beta-> q;
        # lookback: (q, B -> omega) lookback (p, B) iff p -omega-> q
        includes: dict[tuple[int, Nt], list[tuple[int, Nt]]] = {x: [] for x in nt_trans}
        lookback: dict[tuple[int, Production], list[tuple[int, Nt]]] = {}

        for (p, b) in nt_trans:
            for prod in self._cfg.by_lhs.get(b, ()):
                q = p
                for i, s in enumerate(prod.rhs):
                    if isinstance(s, Nt) and (q, s) in includes:
                        rest = prod.rhs[i + 1:]
                        if all(isinstance(t, Nt) and t in self._nullable for t in rest):
                            includes[(q, s)].append((p, b))
                    q = self._goto_state(q, s)
                lookback.setdefault((q, prod), []).append((p, b))

        follow_f = _digraph(nt_trans, lambda x: includes[x], lambda x: read_f[x])

        la: dict[tuple[int, Production], set[int]] = {}
        for (q, prod), xs in lookback.items():
            las = la.setdefault((q, prod), set())
            for x in xs:
                las |= follow_f[x]
        self._la = la

    # table construction

    def build(self) -> LrTables:
        self._build_automaton()
        self._solve_nullable()
        self._solve_lookaheads()

        cfg = self._cfg
        action: list[dict[int, Action]] = []
        conflicts: list[str] = []

        def term_name(t: int) -> str:
            if t == EOF_TERM:
                return '<eof>'
            return cfg.terminals[t].name

        for si, clo in enumerate(self._closures):
            acts: dict[int, list[Action]] = {}

            for t, ni in self._term_goto[si].items():
                acts.setdefault(t, []).append(('s', ni))

            for prod, dot in clo:
                if dot < len(prod.rhs):
                    continue
                if prod is self._aug:
                    acts.setdefault(EOF_TERM, []).append(('acc',))
                    continue
                for t in self._la.get((si, prod), ()):
                    a = ('r', prod.index)
                    if a not in acts.setdefault(t, []):
                        acts[t].append(a)

            row: dict[int, Action] = {}
            for t, aa in acts.items():
                if len(aa) > 1:
                    conflicts.append('\n'.join([
                        f'State {si}, lookahead {term_name(t)}: '
                        f'{" vs ".join(self._render_action(a) for a in aa)}',
                        *[
                            '  ' + _render_item(it)
                            for it in sorted(clo, key=lambda it: (it[0].index, it[1]))
                        ],
                    ]))
                    continue
                row[t] = aa[0]

            action.append(row)

        if conflicts:
            raise AbnfLrConflictError(conflicts)

        return LrTables(
            cfg,
            closures=self._closures,
            action=action,
            goto=self._nt_goto,
        )

    def _render_action(self, a: Action) -> str:
        if a[0] == 's':
            return f'shift({a[1]})'
        elif a[0] == 'r':
            return f'reduce({self._cfg.productions[a[1]]!r})'
        else:
            return 'accept'


def build_tables(cfg: Cfg) -> LrTables:
    return LrTableBuilder(cfg).build()
