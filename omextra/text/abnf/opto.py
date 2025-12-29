import abc
import re
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .base import CompositeOp
from .base import Op
from .grammars import Grammar
from .internal import Regex
from .ops import CaseInsensitiveStringLiteral
from .ops import Concat
from .ops import Either
from .ops import RangeLiteral
from .ops import Repeat
from .ops import RuleRef
from .ops import StringLiteral
from .ops import concat


##


class _RegexOpOptimizer:
    def __init__(self) -> None:
        super().__init__()

        self._dct: dict[Op, _RegexOpOptimizer._Item | None] = {}

    #

    @dc.dataclass(frozen=True)
    class _Item(lang.Abstract):
        @property
        @abc.abstractmethod
        def pat(self) -> str:
            raise NotImplementedError

    @dc.dataclass(frozen=True)
    class _StringLiteral(_Item, lang.Final):
        s: str

        @property
        def pat(self) -> str:
            return re.escape(self.s)

    @dc.dataclass(frozen=True)
    class _CaseInsensitiveStringLiteral(_Item, lang.Final):
        s: str

        @property
        def pat(self) -> str:
            return f'(?i:{re.escape(self.s)})'

    @dc.dataclass(frozen=True)
    class _Regex(_Item, lang.Final):
        ps: str

        @property
        def pat(self) -> str:
            return self.ps

    def _op_to_item(self, op: Op) -> _Item | None:
        if isinstance(op, StringLiteral):
            return _RegexOpOptimizer._StringLiteral(op.value)
        elif isinstance(op, CaseInsensitiveStringLiteral):
            return _RegexOpOptimizer._CaseInsensitiveStringLiteral(op.value)
        elif isinstance(op, Regex):
            return _RegexOpOptimizer._Regex(op.pat.pattern)
        else:
            return None

    #

    def _analyze_single_op(self, op: Op) -> _Item | None:
        if isinstance(op, (StringLiteral, CaseInsensitiveStringLiteral, Regex)):
            return None

        elif isinstance(op, RangeLiteral):
            lo = re.escape(op.value.lo)
            hi = re.escape(op.value.hi)
            return _RegexOpOptimizer._Regex(f'[{lo}-{hi}]')

        elif isinstance(op, RuleRef):
            return None

        elif isinstance(op, Concat):
            children = [self._dct[child] for child in op.children]
            if not all(ca is not None for ca in children):
                # FIXME: merge adjacent
                # if any(ca is not None for ca in children):
                #     breakpoint()
                return None

            return _RegexOpOptimizer._Regex(''.join(check.not_none(ca).pat for ca in children))

        elif isinstance(op, Repeat):
            if (child := self._dct[op.child]) is None:
                if (child := self._op_to_item(op.child)) is None:
                    return None

            # Wrap the child pattern in a non-capturing group if needed to ensure correct quantification. A pattern
            # needs wrapping if it contains multiple elements or operators (e.g., 'ab', 'a|b'). Single character classes
            # [a-z] and# single escaped chars don't need wrapping.
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

            return _RegexOpOptimizer._Regex(child_pat + quantifier)

        elif isinstance(op, Either):
            # Only convert Either if first_match is True, as regex alternation uses first-match semantics. ABNF Either
            # with first_match=False uses longest-match semantics, which differs from regex.
            if not op.first_match:
                return None

            children = [self._dct[child] for child in op.children]
            if not all(ca is not None for ca in children):
                return None

            # Build regex alternation. Use a capturing group for the alternation
            return _RegexOpOptimizer._Regex(f'({"|".join(ca.pat for ca in ta.cast("ta.Sequence[_RegexOpOptimizer._Item]", children))})')  # noqa

        else:
            raise TypeError(op)

    def _analyze_op(self, o: Op) -> None:
        check.not_in(o, self._dct)

        if isinstance(o, CompositeOp):
            for child in o.children:
                self._analyze_op(child)

        self._dct[o] = self._analyze_single_op(o)

    #

    def _transform_single_op(self, op: Op) -> Op:
        item = self._dct[op]

        if item is not None:
            if isinstance(op, Regex):
                return op

            return Regex(re.compile(item.pat))

        if isinstance(op, Concat):
            new_children = tuple(self._transform_single_op(child) for child in op.children)
            if new_children == op.children:
                return op

            return concat(*new_children)

        elif isinstance(op, Repeat):
            new_child = self._transform_single_op(op.child)
            if new_child == op.child:
                return op

            return Repeat(op.times, new_child)

        elif isinstance(op, Either):
            new_children = tuple(self._transform_single_op(child) for child in op.children)
            if new_children == op.children:
                return op

            return Either(*new_children, first_match=op.first_match)

        return op

    def transform_op(self, op: Op) -> Op:
        self._analyze_op(op)

        return self._transform_single_op(op)


##


def optimize_op(op: Op) -> Op:
    op = _RegexOpOptimizer().transform_op(op)

    return op


##


def _inline_insignificant_rules(gram: Grammar) -> Grammar:
    return gram


##


def optimize_grammar(gram: Grammar) -> Grammar:
    gram = _inline_insignificant_rules(gram)

    gram = gram.replace_rules(*[
        r.replace_op(optimize_op(r.op))
        for r in gram.rules
    ])

    return gram
