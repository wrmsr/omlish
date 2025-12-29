"""
TODO:
 - Merge concat
 - Merge concatted literals
 - Regex
"""
import re
import typing as ta

from omlish import check

from .base import Op
from .internal import Regex
from .ops import CaseInsensitiveStringLiteral
from .ops import CompositeOp
from .ops import Concat
from .ops import Either
from .ops import RangeLiteral
from .ops import Repeat
from .ops import RuleRef
from .ops import StringLiteral


##


def _build_op_regex_pat(op: Op, pats_by_op: ta.Mapping[Op, str | None]) -> str | None:
    if isinstance(op, StringLiteral):
        return re.escape(op.value)

    elif isinstance(op, CaseInsensitiveStringLiteral):
        return f'(?i:{re.escape(op.value)})'

    elif isinstance(op, RangeLiteral):
        lo = re.escape(op.value.lo)
        hi = re.escape(op.value.hi)
        return f'[{lo}-{hi}]'

    elif isinstance(op, RuleRef):
        return None

    elif isinstance(op, Regex):
        return op.pat.pattern

    elif isinstance(op, Concat):
        child_pats = [pats_by_op[child] for child in op.children]
        if not all(ca is not None for ca in child_pats):
            return None
        return ''.join(ta.cast(str, ca) for ca in child_pats)

    elif isinstance(op, Repeat):
        if (child_pat := pats_by_op[op.child]) is None:
            return None

        # Wrap the child pattern in a non-capturing group if needed to ensure correct quantification. A pattern needs
        # wrapping if it contains multiple elements or operators (e.g., 'ab', 'a|b'). Single character classes [a-z] and
        # single escaped chars don't need wrapping.
        needs_group = (
            len(child_pat) > 1 and
            not (child_pat.startswith('[') and child_pat.endswith(']'))
        )
        if needs_group:
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

        return child_pat + quantifier

    elif isinstance(op, Either):
        # Only convert Either if first_match is True, as regex alternation uses first-match semantics. ABNF Either with
        # first_match=False uses longest-match semantics, which differs from regex.
        if not op.first_match:
            return None

        child_pats = [pats_by_op[child] for child in op.children]
        if not all(ca is not None for ca in child_pats):
            return None

        # Build regex alternation. Use a capturing group for the alternation
        return f'({"|".join(ta.cast("ta.Sequence[str]", child_pats))})'

    else:
        raise TypeError(op)


def _regex_transform_single_op(op: Op, pats_by_op: ta.Mapping[Op, str | None]) -> Op:
    pat = pats_by_op[op]

    if pat is not None:
        if isinstance(op, Regex):
            return op

        return Regex(re.compile(pat))

    if isinstance(op, Concat):
        new_children = tuple(_regex_transform_single_op(child, pats_by_op) for child in op.children)
        if new_children == op.children:
            return op

        return Concat(*new_children)

    elif isinstance(op, Repeat):
        new_child = _regex_transform_single_op(op.child, pats_by_op)
        if new_child == op.child:
            return op

        return Repeat(op.times, new_child)

    elif isinstance(op, Either):
        new_children = tuple(_regex_transform_single_op(child, pats_by_op) for child in op.children)
        if new_children == op.children:
            return op

        return Either(*new_children, first_match=op.first_match)

    return op


def regex_transform_op(op: Op) -> Op:
    pats_by_op: dict[Op, str | None] = {}

    def analyze_tree(o: Op) -> None:
        check.not_in(o, pats_by_op)

        if isinstance(o, CompositeOp):
            for child in o.children:
                analyze_tree(child)

        pats_by_op[o] = _build_op_regex_pat(o, pats_by_op)

    analyze_tree(op)

    return _regex_transform_single_op(op, pats_by_op)


##


def optimize_op(op: Op) -> Op:
    op = regex_transform_op(op)

    return op
