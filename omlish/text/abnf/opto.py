"""
TODO:
 - origin tracking?
 - minor opts:
  - merge concat(range, range)
"""
import abc
import re
import typing as ta

from ... import check
from ... import dataclasses as dc
from ... import lang
from .analysis import GrammarAnalysis
from .base import CompositeOp
from .base import Op
from .grammars import Channel
from .grammars import Grammar
from .grammars import Rule
from .internal import Regex
from .ops import CaseInsensitiveStringLiteral
from .ops import Concat
from .ops import Either
from .ops import RangeLiteral
from .ops import Repeat
from .ops import RuleRef
from .ops import StringLiteral


##


##
# A convertible subtree contains no RuleRefs (they return None in _regex_item_transform_op), so this analysis is
# entirely local -- no grammar-wide FIRST/FOLLOW fixpoints needed.

# Soundness argument: if the language matched by `op` from a fixed start position is prefix-free (no match is a proper
# prefix of another), there is at most one valid match end per start. re.Pattern.match() finds a match iff one exists,
# so its single greedy match IS the complete match set, and conversion preserves (start, end) semantics in every
# context. `_is_prefix_free` returning False means "can't prove", not "unsafe".


# Inclusive (lo, hi) char ranges. Small sets, so the quadratic intersect is fine.
_CharIntervals: ta.TypeAlias = frozenset[tuple[str, str]]


def _ci_chars(c: str) -> _CharIntervals:
    return frozenset((x, x) for x in {c, c.lower(), c.upper(), c.casefold()} if len(x) == 1)


def _intervals_intersect(a: _CharIntervals, b: _CharIntervals) -> bool:
    return any(al <= bh and bl <= ah for (al, ah) in a for (bl, bh) in b)


def _len_bounds(op: Op) -> tuple[int, int | None]:
    """(min, max) possible match lengths; max=None means unbounded or unknown."""

    if isinstance(op, (StringLiteral, CaseInsensitiveStringLiteral)):
        return (n := len(op.value), n)

    elif isinstance(op, RangeLiteral):
        return (1, 1)

    elif isinstance(op, Concat):
        mns, mxs = zip(*[_len_bounds(c) for c in op.children])
        return (sum(mns), None if any(m is None for m in mxs) else sum(mxs))

    elif isinstance(op, Repeat):
        cmn, cmx = _len_bounds(op.child)
        t = op.times
        return (
            t.min * cmn,
            t.max * cmx if (t.max is not None and cmx is not None) else None,
        )

    elif isinstance(op, Either):
        mns, mxs = zip(*[_len_bounds(c) for c in op.children])
        return (min(mns), None if any(m is None for m in mxs) else max(mxs))

    else:  # RuleRef, Regex: not analyzable
        return (0, None)


def _char_set(op: Op) -> _CharIntervals | None:
    """Over-approximation of all chars appearing in any match; None = unknown."""

    if isinstance(op, StringLiteral):
        return frozenset((c, c) for c in op.value)

    elif isinstance(op, CaseInsensitiveStringLiteral):
        return frozenset().union(*(_ci_chars(c) for c in op.value))

    elif isinstance(op, RangeLiteral):
        return frozenset(((op.value.lo, op.value.hi),))

    elif isinstance(op, (Concat, Either)):
        cs = [_char_set(c) for c in op.children]
        return None if any(c is None for c in cs) else frozenset().union(*cs)  # type: ignore[arg-type]

    elif isinstance(op, Repeat):
        return _char_set(op.child)

    else:
        return None


def _first_chars(op: Op) -> _CharIntervals | None:
    """Over-approximation of chars that can begin a non-empty match; None = unknown."""

    if isinstance(op, StringLiteral):
        return frozenset(((op.value[0], op.value[0]),))

    elif isinstance(op, CaseInsensitiveStringLiteral):
        return _ci_chars(op.value[0])

    elif isinstance(op, RangeLiteral):
        return frozenset(((op.value.lo, op.value.hi),))

    elif isinstance(op, Concat):
        out: _CharIntervals = frozenset()
        for c in op.children:
            if (f := _first_chars(c)) is None:
                return None
            out |= f
            if _len_bounds(c)[0] > 0:  # not nullable: later children can't start it
                return out
        return out

    elif isinstance(op, Either):
        cs = [_first_chars(c) for c in op.children]
        return None if any(c is None for c in cs) else frozenset().union(*cs)  # type: ignore[arg-type]

    elif isinstance(op, Repeat):
        return _first_chars(op.child)

    else:
        return None


def _is_prefix_free(op: Op) -> bool:
    """True if no match of `op` from a fixed start is a proper prefix of another."""

    mn, mx = _len_bounds(op)
    if mx is not None and mn == mx:
        return True  # fixed length: no proper-prefix relations possible

    if isinstance(op, Concat):
        cs = list(op.children)

        # Peel fixed-length leading children: they can't shift the boundary.
        while len(cs) > 1 and (b := _len_bounds(cs[0]))[1] is not None and b[0] == b[1]:
            cs.pop(0)
        if len(cs) == 1:
            return _is_prefix_free(cs[0])

        head, rest = cs[0], (cs[1] if len(cs) == 2 else Concat(*cs[1:]))

        # Repeat(X) then rest, with FIRST(rest) disjoint from chars(X): the boundary is forced by the input, so no match
        # can prefix another. (Proof sketch: if u1·r1 is a proper prefix of u2·r2 with u_i in X*, the char at the
        # shorter boundary lies in FIRST(rest) in one string and in chars(X) in the other -- contradiction; equal
        # boundaries reduce to rest's prefix-freeness.)
        if (
                isinstance(head, Repeat) and
                (hcs := _char_set(head.child)) is not None and
                (rfc := _first_chars(rest)) is not None and
                not _intervals_intersect(hcs, rfc) and
                _len_bounds(rest)[0] > 0 and  # rest must not be nullable
                _is_prefix_free(rest)
        ):
            return True

        return False

    if isinstance(op, Either):
        # Sound if no branch is nullable, each branch is prefix-free, and branches can't prefix each other
        # (pairwise-disjoint first chars).
        fcs = []
        for c in op.children:
            if _len_bounds(c)[0] == 0 or not _is_prefix_free(c):
                return False
            if (f := _first_chars(c)) is None:
                return False
            fcs.append(f)
        return not any(
            _intervals_intersect(fcs[i], fcs[j])
            for i in range(len(fcs))
            for j in range(i + 1, len(fcs))
        )

    if isinstance(op, Repeat):
        return False  # variable-count repeats are extendable by construction

    return False


##


@dc.dataclass(frozen=True)
class _RegexItem(lang.Abstract):
    @property
    @abc.abstractmethod
    def pat(self) -> str:
        raise NotImplementedError

    @classmethod
    def of_op(cls, op: Op) -> _RegexItem | None:
        if isinstance(op, StringLiteral):
            return _StringLiteralRegexItem(op.value)

        elif isinstance(op, CaseInsensitiveStringLiteral):
            return _CaseInsensitiveStringLiteralRegexItem(op.value)

        elif isinstance(op, RangeLiteral):
            lo = re.escape(op.value.lo)
            hi = re.escape(op.value.hi)
            return _RegexRegexItem(f'[{lo}-{hi}]')

        elif isinstance(op, Regex):
            return _RegexRegexItem(op.pat.pattern)

        else:
            return None

    @classmethod
    def of(cls, obj: _RegexItem | Op | None) -> _RegexItem | None:
        if obj is None:
            return None

        elif isinstance(obj, _RegexItem):
            return obj

        elif isinstance(obj, Op):
            return cls.of_op(obj)

        else:
            raise TypeError(obj)


@dc.dataclass(frozen=True)
class _StringLiteralRegexItem(_RegexItem, lang.Final):
    s: str

    @property
    def pat(self) -> str:
        return re.escape(self.s)


@dc.dataclass(frozen=True)
class _CaseInsensitiveStringLiteralRegexItem(_RegexItem, lang.Final):
    s: str

    @property
    def pat(self) -> str:
        return f'(?i:{re.escape(self.s)})'


@dc.dataclass(frozen=True)
class _RegexRegexItem(_RegexItem, lang.Final):
    ps: str

    @property
    def pat(self) -> str:
        return self.ps


def _regex_item_transform_op(op: Op) -> _RegexItem | None:
    if isinstance(op, (StringLiteral, CaseInsensitiveStringLiteral, Regex)):
        return None

    elif isinstance(op, RangeLiteral):
        # Unlike other leafs we eagerly transform RangeLiteral to a regex as it's probably faster than the python impl,
        # even alone.
        return _RegexItem.of_op(op)

    elif isinstance(op, RuleRef):
        return None

    elif isinstance(op, Concat):
        children = [_regex_item_transform_op(child) or _RegexItem.of(child) for child in op.children]
        if all(ca is not None for ca in children):
            return _RegexRegexItem(''.join(check.not_none(ca).pat for ca in children))

        if not any(ca is not None for ca in children):
            return None

        # FIXME: merge adjacent
        return None

    elif isinstance(op, Repeat):
        child = _RegexItem.of(_regex_item_transform_op(op.child))
        if child is None:
            return None

        # Wrap the child pattern in a non-capturing group if needed to ensure correct quantification. A pattern needs
        # wrapping if it contains multiple elements or operators (e.g., 'ab', 'a|b'). Single character classes [a-z] and
        # single escaped chars don't need wrapping.
        if (
                len(child_pat := child.pat) > 1 and
                not (child_pat.startswith('[') and child_pat.endswith(']'))
        ):
            child_pat = f'(?:{child_pat})'

        times = op.times
        if times.min == 0 and times.max is None:
            quantifier = '*'
        elif times.min == 1 and times.max is None:
            quantifier = '+'
        elif times.min == 0 and times.max == 1:
            quantifier = '?'
        elif times.max is None:
            quantifier = f'{{{times.min},}}'
        elif times.min == times.max:
            quantifier = f'{{{times.min}}}'
        else:
            quantifier = f'{{{times.min},{times.max}}}'

        return _RegexRegexItem(child_pat + quantifier)

    elif isinstance(op, Either):
        # Regex alternation is ordered-first-match, so a first_match=False (all-matches) Either is only convertible
        # when branch order provably can't matter: all branches having the same fixed length means at most one span per
        # start, and acceptance is the plain union of branches. (This covers the ubiquitous char-class alternations
        # like ALPHA = %x41-5A / %x61-7A.)
        if not op.first_match:
            lbs = [_len_bounds(c) for c in op.children]
            if not all(mx is not None and mn == mx == lbs[0][0] for mn, mx in lbs):
                return None

        children = [_regex_item_transform_op(child) or _RegexItem.of(child) for child in op.children]
        if all(ca is not None for ca in children):
            if op.first_match:
                # An atomic group: plain regex alternation backtracks into later branches when the rest of the pattern
                # fails, but interpreted first_match COMMITS to the first matching branch. (?>...) reproduces that
                # commit.
                grp = '(?>'
            else:
                grp = '(?:'
            return _RegexRegexItem(''.join([
                grp,
                '|'.join(check.not_none(ca).pat for ca in children),
                ')',
            ]))

        if not any(ca is not None for ca in children):
            return None

        # FIXME: merge adjacent
        return None

    else:
        raise TypeError(op)


def _regex_transform_op(op: Op, *, no_gate: bool = False) -> Op:
    if not no_gate and not _is_prefix_free(op):
        return op
    v = _regex_item_transform_op(op)

    if v is None:
        return op

    elif isinstance(v, _RegexItem):
        return Regex(re.compile(v.pat))

    else:
        raise TypeError(v)


##


def optimize_op(op: Op) -> Op:
    """
    Converts `op` to a single Regex where that is provably span-preserving, otherwise recurses to convert maximal
    provable subtrees, leaving the surrounding structure interpreted.
    """

    if (n := _regex_transform_op(op)) is not op:
        return n

    if isinstance(op, CompositeOp):
        return op.replace_children(*[optimize_op(c) for c in op.children])

    return op


##


def _inline_rules(fn: ta.Callable[[Rule], bool], gram: Grammar) -> Grammar:
    cur_rule: Rule
    inlined_rules: dict[str, Op] = {}

    def rec_op(op: Op) -> Op:
        if isinstance(op, RuleRef):
            if op.name_f == cur_rule.name_f:
                return op

            if (r := gram.rule(op.name)) is None or not fn(r):
                return op

            try:
                return inlined_rules[r.name]
            except KeyError:
                pass

            inlined_rules[op.name] = op
            i_op = rec_op(r.op)
            inlined_rules[op.name] = i_op

            return op.coalesce(i_op)

        elif isinstance(op, CompositeOp):
            return op.replace_children(*map(rec_op, op.children))

        else:
            return op

    new_rules: list[Rule] = []
    for rule in gram.rules:
        cur_rule = rule
        new_rules.append(rule.replace_op(rec_op(rule.op)))

    return gram.replace_rules(*new_rules)


##


def optimize_grammar(
        gram: Grammar,
        *,
        inline_channels: ta.Container[Channel] | None = (Channel.SPACE,),
        parse_only: bool = False,
) -> Grammar:
    """
    Contract:

    By default the optimized grammar produces the same match *spans* per (op, start) as the unoptimized one - regex
    conversion only happens where the subtree's language is provably prefix-free, so `iter_parse` results are preserved
    (modulo internal tree structure below converted nodes, which becomes opaque).

    With `parse_only=True`, conversion is additionally allowed wherever the grammar-wide FIRST/FOLLOW analysis proves it
    preserves `Grammar.parse()` results - longest match from the grammar root. Shorter alternatives that `iter_parse`
    would have yielded may be lost; only use this when consuming grammars exclusively via `parse()`.
    """

    if inline_channels:
        gram = _inline_rules(lambda r: r.channel in inline_channels, gram)

    anl: GrammarAnalysis | None = None
    if parse_only:
        anl = GrammarAnalysis(gram)

    new_rules: list[Rule] = []
    for r in gram.rules:
        op = r.op
        if anl is not None and anl.safe_to_convert(r):
            op = _regex_transform_op(op, no_gate=True)
        if op is r.op:
            op = optimize_op(op)
        new_rules.append(r.replace_op(op))

    return gram.replace_rules(*new_rules)
