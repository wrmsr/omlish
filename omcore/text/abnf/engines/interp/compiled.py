"""
Closure-compilation of op trees for the interpreter engine.

Each op node compiles to a plain function `(state, start) -> tuple[Match, ...]` capturing its children's compiled
functions in closure cells - eliminating per-visit dispatch dict lookups, context tuple allocation, and generator
frames, which dominate the reference implementation's runtime. Semantics are intended to be *identical* to the
reference `parsers._ParserImpl` (same match sets, same yield order); the differential tests enforce this.

Rule bodies are compiled and memoized once per (casefolded) rule name, so distinct `RuleRef` instances naming the same
rule share both work and memo entries (the reference impl memoizes per ref-site op identity). Consequently `Match.op`
for rule-ref nodes is a per-name canonical `RuleRef` rather than the specific ref-site instance - all consumers key off
`RuleRef.name`, not instance identity.

Parse state (memo, furthest position, rule stack) lives on a single inspectable `ParseState` object - a deliberate
debugging affordance, not just an implementation detail.

Hot-path notes: memoization is fused into each composite's closure rather than layered as a wrapper (halves call
depth), memo keys are packed ints rather than tuples, step accounting is inline attribute arithmetic against a maxsize
default, and Match sequences are built with list comprehensions.
"""
import sys
import typing as ta

from ..... import check
from ...analysis import GrammarAnalysis
from ...base import CompositeOp
from ...base import Op
from ...errors import AbnfMaxStepsExceededError
from ...grammars import Grammar
from ...internal import Regex
from ...matches import Match
from ...ops import CaseInsensitiveStringLiteral
from ...ops import Concat
from ...ops import Either
from ...ops import RangeLiteral
from ...ops import Repeat
from ...ops import RuleRef
from ...ops import StringLiteral


OpFn: ta.TypeAlias = ta.Callable[['ParseState', int], tuple[Match, ...]]


##


# Memo keys are `(op_id << _MEMO_KEY_SHIFT) | start` - a single int hashes and allocates cheaper than a tuple.
_MEMO_KEY_SHIFT = 40


class ParseState:
    """Per-parse mutable state. Deliberately inspectable - attach a debugger and poke at it."""

    __slots__ = (
        'source',
        'max_steps',
        'memo',
        'furthest_end',
        'furthest_trace',
        'rule_stack',
        'steps',
    )

    def __init__(
            self,
            source: str,
            *,
            max_steps: int | None = None,
    ) -> None:
        super().__init__()

        if len(source) >= (1 << _MEMO_KEY_SHIFT):
            raise ValueError('Source too large')

        self.source = source
        self.max_steps = max_steps if max_steps is not None else sys.maxsize

        self.memo: dict[int, tuple[Match, ...]] = {}

        self.furthest_end = -1
        self.furthest_trace: tuple[str, ...] = ()

        self.rule_stack: list[str] = []

        self.steps = 0


##


class GrammarCompiler:
    def __init__(self, grammar: Grammar) -> None:
        super().__init__()

        self._grammar = grammar

        self._analysis = GrammarAnalysis(grammar)

        self._next_memo_id = 0

        # Per rule name: a mutable cell later filled with the rule's memoized body fn (rules may be mutually
        # recursive, so ref-site closures must late-bind), and the memoized ref-site wrapper fn shared by every
        # RuleRef of that name.
        self._rule_body_cells: dict[str, list] = {}
        self._rule_ref_fns: dict[str, OpFn] = {}

        self._rule_fns: dict[str, OpFn] = {}

        for n in grammar.rules.rules_by_name_f:
            self._compile_rule_body(n)

    def _fresh_memo_id(self) -> int:
        i = self._next_memo_id
        self._next_memo_id += 1
        return i

    def rule_fn(self, name_f: str) -> OpFn:
        return self._rule_fns[name_f]

    #

    def _compile_rule_body(self, name_f: str) -> OpFn:
        try:
            return self._rule_fns[name_f]
        except KeyError:
            pass

        rule = self._grammar.rules.rules_by_name_f[name_f]

        cell = self._rule_body_cells.get(name_f)
        if cell is None:
            cell = self._rule_body_cells[name_f] = [None]
            cell[0] = self._compile_op(rule.op)

        rule_name = rule.name

        def f(st: ParseState, start: int) -> tuple[Match, ...]:
            st.rule_stack.append(rule_name)
            try:
                return cell[0](st, start)
            finally:
                st.rule_stack.pop()

        self._rule_fns[name_f] = f
        return f

    def _compile_rule_ref(self, op: RuleRef) -> OpFn:
        name_f = op._name_f  # noqa
        try:
            return self._rule_ref_fns[name_f]
        except KeyError:
            pass

        rule = self._grammar.rules.rules_by_name_f[name_f]

        cell = self._rule_body_cells.get(name_f)
        if cell is None:
            # Compile the body lazily via _compile_rule_body's cell machinery.
            self._compile_rule_body(name_f)
            cell = check.not_none(self._rule_body_cells.get(name_f))

        rule_name = rule.name
        mk = self._fresh_memo_id() << _MEMO_KEY_SHIFT

        def f(st: ParseState, start: int) -> tuple[Match, ...]:
            memo = st.memo
            if (v := memo.get(key := mk | start)) is not None:
                return v
            st.steps = steps = st.steps + 1
            if steps > st.max_steps:
                raise AbnfMaxStepsExceededError(steps)
            st.rule_stack.append(rule_name)
            try:
                bms = cell[0](st, start)
            finally:
                st.rule_stack.pop()
            v = tuple([Match(op, cm.start, cm.end, (cm,)) for cm in bms])
            memo[key] = v
            return v

        self._rule_ref_fns[name_f] = f
        return f

    #

    def _compile_string_literal(self, op: StringLiteral) -> OpFn:
        value = op._value  # noqa
        n = len(value)

        def f(st: ParseState, start: int) -> tuple[Match, ...]:
            if st.source.startswith(value, start):
                end = start + n
                if end > st.furthest_end:
                    st.furthest_end = end
                    st.furthest_trace = tuple(st.rule_stack)
                return (Match(op, start, end, ()),)
            return ()

        return f

    def _compile_case_insensitive_string_literal(self, op: CaseInsensitiveStringLiteral) -> OpFn:
        value = op._value  # noqa  # stored casefolded
        vn = len(value)

        def f(st: ParseState, start: int) -> tuple[Match, ...]:
            source = st.source

            # Fast path: casefold never shrinks, so a folded vn-char slice of length vn means no char expanded and the
            # per-char fold agrees with the slice fold.
            s = source[start:start + vn]
            folded = s.casefold()
            if len(folded) == vn and len(s) == vn:
                if folded == value:
                    end = start + vn
                    if end > st.furthest_end:
                        st.furthest_end = end
                        st.furthest_trace = tuple(st.rule_stack)
                    return (Match(op, start, end, ()),)
                return ()

            # Slow path: fold char by char, taking end from raw source chars consumed ('\xdf' -> 'ss' etc).
            end = start
            folded = ''
            while len(folded) < vn:
                if end >= len(source):
                    return ()
                folded += source[end].casefold()
                end += 1
            if folded == value:
                if end > st.furthest_end:
                    st.furthest_end = end
                    st.furthest_trace = tuple(st.rule_stack)
                return (Match(op, start, end, ()),)
            return ()

        return f

    def _compile_range_literal(self, op: RangeLiteral) -> OpFn:
        lo = op._value.lo  # noqa
        hi = op._value.hi  # noqa

        def f(st: ParseState, start: int) -> tuple[Match, ...]:
            source = st.source
            if start < len(source) and lo <= source[start] <= hi:
                end = start + 1
                if end > st.furthest_end:
                    st.furthest_end = end
                    st.furthest_trace = tuple(st.rule_stack)
                return (Match(op, start, end, ()),)
            return ()

        return f

    def _compile_regex(self, op: Regex) -> OpFn:
        pat_match = op._pat.match  # noqa

        def f(st: ParseState, start: int) -> tuple[Match, ...]:
            if (m := pat_match(st.source, start)) is not None:
                end = m.end()
                if end > st.furthest_end:
                    st.furthest_end = end
                    st.furthest_trace = tuple(st.rule_stack)
                return (Match(op, start, end, ()),)
            return ()

        return f

    def _compile_concat(self, op: Concat) -> OpFn:
        cfs = [self._compile_op(c) for c in op._children]  # noqa
        mk = self._fresh_memo_id() << _MEMO_KEY_SHIFT

        def f(st: ParseState, start: int) -> tuple[Match, ...]:
            memo = st.memo
            if (v := memo.get(key := mk | start)) is not None:
                return v
            st.steps = steps = st.steps + 1
            if steps > st.max_steps:
                raise AbnfMaxStepsExceededError(steps)

            match_tups: list[tuple[Match, ...]] = [()]
            for cf in cfs:
                next_match_tups: list[tuple[Match, ...]] = []
                for mt in match_tups:
                    for cm in cf(st, mt[-1].end if mt else start):
                        next_match_tups.append((*mt, cm))
                if not next_match_tups:
                    memo[key] = ()
                    return ()
                match_tups = next_match_tups

            v = tuple([Match(op, start, mt[-1].end, mt) for mt in match_tups])
            memo[key] = v
            return v

        return f

    _EITHER_DISPATCH_MIN_BRANCHES: ta.ClassVar[int] = 4
    _EITHER_DISPATCH_MAX_CHARS: ta.ClassVar[int] = 256

    def _build_either_dispatch(self, op: Either, cfs: ta.Sequence[OpFn]) -> tuple[dict[str, tuple[OpFn, ...]], tuple[OpFn, ...]] | None:  # noqa
        """
        Predictive branch dispatch: a branch that is non-nullable and whose FIRST set provably excludes the next source
        char cannot match there, so it need not be tried at all. Returns (char -> ordered branch fns, fallback fns for
        chars outside every computed FIRST set - which are also the only viable branches at EOF), or None when no
        branch has a usably small FIRST set.
        """

        if len(cfs) < self._EITHER_DISPATCH_MIN_BRANCHES:
            return None

        anl = self._analysis

        infos: list[tuple[ta.Any, OpFn]] = []  # (CharSet | None, fn); None = must always be tried
        for c, cf in zip(op._children, cfs):  # noqa
            if anl.op_nullable(c):
                infos.append((None, cf))
                continue
            fs = anl.op_first(c)
            if not (0 < len(fs) <= self._EITHER_DISPATCH_MAX_CHARS):
                infos.append((None, cf))
            else:
                infos.append((fs, cf))

        if all(fs is None for fs, _ in infos):
            return None

        all_chars: set[str] = set()
        for fs, _ in infos:
            if fs is not None:
                for lo, hi in fs.intervals:
                    all_chars.update(map(chr, range(lo, hi + 1)))

        dispatch = {
            ch: tuple(cf for fs, cf in infos if fs is None or ch in fs)
            for ch in all_chars
        }
        always = tuple(cf for fs, cf in infos if fs is None)
        return (dispatch, always)

    def _compile_either(self, op: Either) -> OpFn:
        cfs = [self._compile_op(c) for c in op._children]  # noqa
        first_match = op._first_match  # noqa
        mk = self._fresh_memo_id() << _MEMO_KEY_SHIFT

        dsp = self._build_either_dispatch(op, cfs)

        if dsp is not None:
            dispatch, always = dsp

            def df(st: ParseState, start: int) -> tuple[Match, ...]:
                memo = st.memo
                if (v := memo.get(key := mk | start)) is not None:
                    return v
                st.steps = steps = st.steps + 1
                if steps > st.max_steps:
                    raise AbnfMaxStepsExceededError(steps)

                source = st.source
                if start < len(source):
                    fns = dispatch.get(source[start], always)
                else:
                    fns = always

                out: list[Match] = []
                for cf in fns:
                    cms = cf(st, start)
                    if cms:
                        out.extend([Match(op, start, cm.end, (cm,)) for cm in cms])
                        if first_match:
                            break

                v = tuple(out)
                memo[key] = v
                return v

            return df

        cfs_t = tuple(cfs)

        def f(st: ParseState, start: int) -> tuple[Match, ...]:
            memo = st.memo
            if (v := memo.get(key := mk | start)) is not None:
                return v
            st.steps = steps = st.steps + 1
            if steps > st.max_steps:
                raise AbnfMaxStepsExceededError(steps)

            out: list[Match] = []
            for cf in cfs_t:
                cms = cf(st, start)
                if cms:
                    out.extend([Match(op, start, cm.end, (cm,)) for cm in cms])
                    if first_match:
                        break

            v = tuple(out)
            memo[key] = v
            return v

        return f

    def _compile_repeat(self, op: Repeat) -> OpFn:
        cf = self._compile_op(op._child)  # noqa
        times_min = op._times.min  # noqa
        times_max = op._times.max  # noqa
        mk = self._fresh_memo_id() << _MEMO_KEY_SHIFT

        def f(st: ParseState, start: int) -> tuple[Match, ...]:
            memo = st.memo
            if (v := memo.get(key := mk | start)) is not None:
                return v

            # Same frontier algorithm as the reference impl, but iterating only the current frontier instead of
            # rescanning all accumulated (count, pos) entries each round.
            matches_by_count_pos: dict[tuple[int, int], tuple[Match, ...]] = {(0, start): ()}
            seen_ends: set[int] = {start}
            frontier: dict[int, tuple[Match, ...]] = {start: ()}

            i = 0
            while True:
                if times_max is not None and i == times_max:
                    break

                st.steps = steps = st.steps + 1
                if steps > st.max_steps:
                    raise AbnfMaxStepsExceededError(steps)

                next_frontier: dict[int, tuple[Match, ...]] = {}
                for end_pos, mt in frontier.items():
                    for cm in cf(st, end_pos):
                        if (ne := cm.end) not in next_frontier:
                            next_frontier[ne] = (*mt, cm)

                if not next_frontier:
                    break

                i += 1
                for ne, nmt in next_frontier.items():
                    matches_by_count_pos[(i, ne)] = nmt
                frontier = next_frontier

                # Termination: see the reference impl for the argument.
                new_ends = set(next_frontier) - seen_ends
                seen_ends |= new_ends
                if not new_ends and i >= times_min:
                    break

            if i < times_min:
                memo[key] = ()
                return ()

            mx = times_max if times_max is not None else i
            valid = [
                (end_pos, count, mt)
                for (count, end_pos), mt in matches_by_count_pos.items()
                if times_min <= count <= mx
            ]
            valid.sort(key=lambda x: (x[0], x[1]), reverse=True)

            v = tuple([Match(op, start, end_pos, mt) for end_pos, _, mt in valid])
            memo[key] = v
            return v

        return f

    #

    def _compile_op(self, op: Op) -> OpFn:
        if isinstance(op, StringLiteral):
            return self._compile_string_literal(op)
        elif isinstance(op, CaseInsensitiveStringLiteral):
            return self._compile_case_insensitive_string_literal(op)
        elif isinstance(op, RangeLiteral):
            return self._compile_range_literal(op)
        elif isinstance(op, Regex):
            return self._compile_regex(op)
        elif isinstance(op, Concat):
            return self._compile_concat(op)
        elif isinstance(op, Either):
            return self._compile_either(op)
        elif isinstance(op, Repeat):
            return self._compile_repeat(op)
        elif isinstance(op, RuleRef):
            return self._compile_rule_ref(op)
        elif isinstance(op, CompositeOp):
            raise TypeError(op)
        else:
            raise TypeError(op)


##


class CompiledRules:
    """The product of closure-compiling a grammar: one entrypoint fn per rule, shared compiled innards."""

    def __init__(self, grammar: Grammar) -> None:
        super().__init__()

        self._grammar = grammar

        gc = GrammarCompiler(grammar)
        self._rule_fns: ta.Mapping[str, OpFn] = {n: gc.rule_fn(n) for n in grammar.rules.rules_by_name_f}

    @property
    def grammar(self) -> Grammar:
        return self._grammar

    def match_rule(
            self,
            state: ParseState,
            rule_name_f: str,
            start: int,
    ) -> tuple[Match, ...]:
        return self._rule_fns[rule_name_f](state, start)
