"""
grammar-wide nullability / FIRST / FOLLOW analysis over CharSets, and the regex-conversion safety predicate it enables:

    safe_to_convert(rule)  <=>  EXTEND(rule.op) & FOLLOW(rule) == EMPTY

where EXTEND(op) over-approximates the set of characters that can extend some match of `op` into a longer match of `op`
from the same start. Note EXTEND(op) == EMPTY iff op's language is prefix-free -- the "quick option 2" gate is exactly
that special case; this generalizes it with grammar context.

Soundness: if the interpreter would have used a shorter match ending at e, the overall parse consumes source[e] via
whatever follows -- so source[e] is in FOLLOW. The greedy regex extended past e, so source[e] is in EXTEND. Disjointness
makes that impossible, hence the greedy end is the only usable one.

Contract (decide this explicitly!): the analysis preserves `Grammar.parse()` results -- longest match at the root -- not
the full `iter_parse()` match multiset. Accordingly the root rule contributes FOLLOW = EMPTY: any shorter root match is
dominated by the greedy one under longest-match. If callers may parse with `root=<other rule>`, the
union-over-call-sites FOLLOW we compute for that rule is a superset of its FOLLOW-as-root (EMPTY), so the check stays
sound.

All three rule-level maps are least fixpoints, solved by naive round-robin iteration -- grammars are tiny and CharSet
equality is structural, so this terminates fast (the lattice has finite height per grammar alphabet).

Integration into opto.py:

    def optimize_grammar(grammar, *, inline_channels=frozenset([Channel.SPACE])):
        g2 = <inline pass as today>
        anl = GrammarAnalysis(g2)
        return Grammar(
            *[
                r.replace_op(_regex_transform_op(r.op)) if anl.safe_to_convert(r) else r
                for r in g2.rules
            ],
            root=...,
        )

Rules the analysis can't prove safe keep interpreted semantics (or, later, get the endpos-enumerating Regex variant).
"""
import typing as ta

from .base import Op
from .charsets import CharSet
from .grammars import Grammar
from .grammars import Rule
from .ops import CaseInsensitiveStringLiteral
from .ops import Concat
from .ops import Either
from .ops import RangeLiteral
from .ops import Repeat
from .ops import RuleRef
from .ops import StringLiteral


##


def _is_fixed_len(mn: int, mx: int | None) -> bool:
    return mx is not None and mn == mx


class GrammarAnalysis:
    def __init__(self, grammar: Grammar) -> None:
        super().__init__()

        self._grammar = grammar
        self._rules: ta.Mapping[str, Rule] = grammar.rules.rules_by_name_f

        self._nullable: dict[str, bool] = {n: False for n in self._rules}
        self._first: dict[str, CharSet] = {n: CharSet.EMPTY for n in self._rules}
        self._char_set: dict[str, CharSet] = {n: CharSet.EMPTY for n in self._rules}
        self._follow: dict[str, CharSet] = {n: CharSet.EMPTY for n in self._rules}

        self._solve()

    # per-op queries (consult the rule tables for RuleRefs)

    def op_nullable(self, op: Op) -> bool:
        if isinstance(op, (StringLiteral, CaseInsensitiveStringLiteral, RangeLiteral)):
            return False  # literals are non-empty by construction
        elif isinstance(op, Concat):
            return all(self.op_nullable(c) for c in op.children)
        elif isinstance(op, Either):
            return any(self.op_nullable(c) for c in op.children)
        elif isinstance(op, Repeat):
            return op.times.min == 0 or self.op_nullable(op.child)
        elif isinstance(op, RuleRef):
            return self._nullable[op.name_f]
        else:  # Regex etc.: unknown -> assume nullable (conservative for FOLLOW prop)
            return True

    def op_first(self, op: Op) -> CharSet:
        """Chars that can begin a non-empty match."""

        if isinstance(op, StringLiteral):
            return CharSet.of_chars(op.value[0])
        elif isinstance(op, CaseInsensitiveStringLiteral):
            return CharSet.of_chars(op.value[0]).fold_case()
        elif isinstance(op, RangeLiteral):
            return CharSet.of_range(op.value.lo, op.value.hi)
        elif isinstance(op, Concat):
            out = CharSet.EMPTY
            for c in op.children:
                out |= self.op_first(c)
                if not self.op_nullable(c):
                    break
            return out
        elif isinstance(op, Either):
            out = CharSet.EMPTY
            for c in op.children:
                out |= self.op_first(c)
            return out
        elif isinstance(op, Repeat):
            return self.op_first(op.child)
        elif isinstance(op, RuleRef):
            return self._first[op.name_f]
        else:
            return CharSet.ANY  # unknown

    def op_char_set(self, op: Op) -> CharSet:
        """Chars appearing anywhere in any match (crude EXTEND fallback)."""

        if isinstance(op, StringLiteral):
            return CharSet.of_chars(op.value)
        elif isinstance(op, CaseInsensitiveStringLiteral):
            return CharSet.of_chars(op.value).fold_case()
        elif isinstance(op, RangeLiteral):
            return CharSet.of_range(op.value.lo, op.value.hi)
        elif isinstance(op, (Concat, Either)):
            out = CharSet.EMPTY
            for c in op.children:
                out |= self.op_char_set(c)
            return out
        elif isinstance(op, Repeat):
            return self.op_char_set(op.child)
        elif isinstance(op, RuleRef):
            return self._char_set[op.name_f]
        else:
            return CharSet.ANY

    def op_len_bounds(self, op: Op) -> tuple[int, int | None]:
        if isinstance(op, (StringLiteral, CaseInsensitiveStringLiteral)):
            return (n := len(op.value), n)
        elif isinstance(op, RangeLiteral):
            return (1, 1)
        elif isinstance(op, Concat):
            mns, mxs = zip(*[self.op_len_bounds(c) for c in op.children])
            return (sum(mns), None if any(m is None for m in mxs) else sum(mxs))
        elif isinstance(op, Repeat):
            cmn, cmx = self.op_len_bounds(op.child)
            t = op.times
            return (
                t.min * cmn,
                t.max * cmx if (t.max is not None and cmx is not None) else None,
            )
        elif isinstance(op, Either):
            mns, mxs = zip(*[self.op_len_bounds(c) for c in op.children])
            return (min(mns), None if any(m is None for m in mxs) else max(mxs))
        else:  # RuleRef: could add a fixpoint pass for rule length bounds; TODO
            return (0, None)

    # EXTEND: chars that can grow some match of `op` into a longer one

    def op_extend(self, op: Op) -> CharSet:
        mn, mx = self.op_len_bounds(op)
        if _is_fixed_len(mn, mx):
            return CharSet.EMPTY

        if isinstance(op, Repeat):
            # growth by another repetition begins with FIRST(child); growth within the last repetition is EXTEND(child).
            # (Bounded max is ignored -- over-approximate.)
            return self.op_first(op.child) | self.op_extend(op.child)

        if isinstance(op, Concat):
            cs = list(op.children)

            # fixed-length leading children can't shift the boundary
            while len(cs) > 1 and _is_fixed_len(*self.op_len_bounds(cs[0])):
                cs.pop(0)
            if len(cs) == 1:
                return self.op_extend(cs[0])

            head, rest = cs[0], (cs[1] if len(cs) == 2 else Concat(*cs[1:]))

            # forced boundary: Repeat(X) then rest, chars(X) disjoint from FIRST(rest), rest non-nullable -> only
            # rest-internal extension
            if (
                    isinstance(head, Repeat) and
                    self.op_char_set(head.child).isdisjoint(self.op_first(rest)) and
                    not self.op_nullable(rest)
            ):
                return self.op_extend(rest)

            # crude fallback: any char of the whole op (always sound: extension chars lie inside some longer match)
            return self.op_char_set(op)

        if isinstance(op, Either):
            out = CharSet.EMPTY
            cross = False
            firsts = []
            for c in op.children:
                out |= self.op_extend(c)
                if self.op_nullable(c):
                    cross = True  # empty match is a prefix of everything
                firsts.append(self.op_first(c))
            if not cross:
                cross = any(
                    not firsts[i].isdisjoint(firsts[j])
                    for i in range(len(firsts))
                    for j in range(i + 1, len(firsts))
                )
            if cross:
                out |= self.op_char_set(op)  # crude cross-branch bound
            return out

        if isinstance(op, RuleRef):
            return self.op_extend(self._rules[op.name_f].op)

        return CharSet.ANY  # unknown op kind

    # rule-level fixpoints

    def _solve(self) -> None:
        # nullability, FIRST, and char-set converge independently of FOLLOW
        while True:
            changed = False
            for n, r in self._rules.items():
                if (b := self.op_nullable(r.op)) != self._nullable[n]:
                    self._nullable[n] = b
                    changed = True
                if (f := self.op_first(r.op)) != self._first[n]:
                    self._first[n] = f
                    changed = True
                if (c := self.op_char_set(r.op)) != self._char_set[n]:
                    self._char_set[n] = c
                    changed = True
            if not changed:
                break

        # FOLLOW: walk every rule body threading a follow-context down to each RuleRef occurrence. Root contributes
        # EMPTY (see contract note above).
        def walk(op: Op, ctx: CharSet) -> None:
            if isinstance(op, RuleRef):
                n = op.name_f
                if (u := self._follow[n] | ctx) != self._follow[n]:
                    self._follow[n] = u
                    self._dirty = True

            elif isinstance(op, Concat):
                cs = op.children
                for i, c in enumerate(cs):
                    # follow of position i: FIRSTs of the nullable run after it, plus outer ctx if everything after is
                    # nullable
                    acc = CharSet.EMPTY
                    thru = True
                    for d in cs[i + 1:]:
                        acc |= self.op_first(d)
                        if not self.op_nullable(d):
                            thru = False
                            break
                    walk(c, acc | ctx if thru else acc)

            elif isinstance(op, Either):
                for c in op.children:
                    walk(c, ctx)

            elif isinstance(op, Repeat):
                t = op.times
                self_follow = (
                    self.op_first(op.child)
                    if (t.max is None or t.max > 1)
                    else CharSet.EMPTY
                )
                walk(op.child, ctx | self_follow)

        while True:
            self._dirty = False
            for r in self._rules.values():
                walk(r.op, self._follow[r.name_f])
            if not self._dirty:
                break

    # public results

    def rule_follow(self, rule: Rule | str) -> CharSet:
        n = rule.name_f if isinstance(rule, Rule) else rule.casefold()
        return self._follow[n]

    def safe_to_convert(self, rule: Rule | str) -> bool:
        r = rule if isinstance(rule, Rule) else self._rules[rule.casefold()]
        return self.op_extend(r.op).isdisjoint(self.rule_follow(r))
