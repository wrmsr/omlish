"""
TODO:
 - origin tracking?
 - minor opts:
  - merge concat(range, range)
"""
import abc
import re
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

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


@dc.dataclass(frozen=True)
class _RegexItem(lang.Abstract):
    @property
    @abc.abstractmethod
    def pat(self) -> str:
        raise NotImplementedError

    @classmethod
    def of_op(cls, op: Op) -> ta.Optional['_RegexItem']:
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
    def of(cls, obj: ta.Union['_RegexItem', Op, None]) -> ta.Optional['_RegexItem']:
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
        # Only convert Either if first_match is True, as regex alternation uses first-match semantics. ABNF Either with
        # first_match=False uses longest-match semantics, which differs from regex.
        if not op.first_match:
            return None

        children = [_regex_item_transform_op(child) or _RegexItem.of(child) for child in op.children]
        if all(ca is not None for ca in children):
            # Build regex alternation. Use a capturing group for the alternation
            return _RegexRegexItem(''.join([
                '(',
                '|'.join(check.not_none(ca).pat for ca in children),
                ')',
            ]))

        if not any(ca is not None for ca in children):
            return None

        # FIXME: merge adjacent
        return None

    else:
        raise TypeError(op)


def _regex_transform_op(op: Op) -> Op:
    v = _regex_item_transform_op(op)

    if v is None:
        return op

    elif isinstance(v, _RegexItem):
        return Regex(re.compile(v.pat))

    else:
        raise TypeError(v)


##


def optimize_op(op: Op) -> Op:
    op = _regex_transform_op(op)

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
) -> Grammar:
    if inline_channels:
        gram = _inline_rules(lambda r: r.channel in inline_channels, gram)

    gram = gram.replace_rules(*[
        r.replace_op(optimize_op(r.op))
        for r in gram.rules
    ])

    return gram
