import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .base import LeafOp
from .base import Op


##


class Literal(LeafOp, lang.Abstract):
    def _match_repr(self) -> str:
        return repr(self)


@ta.final
class StringLiteral(Literal, lang.Final):
    def __init__(self, value: str) -> None:
        super().__init__()

        self._value = check.non_empty_str(value)

    @property
    def value(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._value!r})'


@ta.final
class CaseInsensitiveStringLiteral(Literal, lang.Final):
    def __init__(self, value: str) -> None:
        super().__init__()

        self._value = check.non_empty_str(value).casefold()

    @property
    def value(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._value!r})'


@ta.final
class RangeLiteral(Literal, lang.Final):
    @dc.dataclass(frozen=True)
    class Range:
        lo: str
        hi: str

        def __post_init__(self) -> None:
            check.non_empty_str(self.lo)
            check.non_empty_str(self.hi)
            check.state(self.hi >= self.lo)

    def __init__(self, value: Range) -> None:
        super().__init__()

        self._value = check.isinstance(value, RangeLiteral.Range)

    @property
    def value(self) -> Range:
        return self._value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._value!r})'


@ta.overload
def literal(s: str, *, case_sensitive: bool = False) -> StringLiteral:
    ...


@ta.overload
def literal(lo: str, hi: str) -> RangeLiteral:
    ...


def literal(*args, case_sensitive=None):
    if not args:
        raise TypeError
    elif len(args) == 1:
        s = check.isinstance(check.single(args), str)
        if case_sensitive:
            return StringLiteral(s)
        else:
            return CaseInsensitiveStringLiteral(s)
    elif len(args) == 2:
        check.none(case_sensitive)
        return RangeLiteral(RangeLiteral.Range(*map(check.of_isinstance(str), args)))
    else:
        raise TypeError(args)


##


@ta.final
class Concat(Op, lang.Final):
    def __init__(self, *children: Op) -> None:
        super().__init__()

        for c in check.not_empty(children):
            check.isinstance(c, Op)
        self._children = children

    @property
    def children(self) -> ta.Sequence[Op]:
        return self._children

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({", ".join(map(repr, self._children))})'


concat = Concat


##


@ta.final
class Repeat(Op, lang.Final):
    @dc.dataclass(frozen=True)
    class Times:
        min: int = 0
        max: int | None = None

        def __post_init__(self) -> None:
            if self.max is not None:
                check.state(self.max >= self.min)

        def __repr__(self) -> str:
            if not self.min and self.max is None:
                s = '*'
            elif not self.min and self.max == 1:
                s = '?'
            elif self.min and self.max is None:
                s = f'{self.min}+'
            else:
                s = f'{self.min}-{self.max!r}'
            return f'{self.__class__.__name__}({s})'

    def __init__(self, times: Times, child: Op) -> None:
        super().__init__()

        self._times = check.isinstance(times, Repeat.Times)
        self._child = check.isinstance(child, Op)

    @property
    def times(self) -> Times:
        return self._times

    @property
    def child(self) -> Op:
        return self._child

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._times}, {self._child!r})'


@ta.overload
def repeat(child: Op) -> Repeat:  # noqa
    ...


@ta.overload
def repeat(times: Repeat.Times, child: Op) -> Repeat:  # noqa
    ...


@ta.overload
def repeat(min: int, child: Op) -> Repeat:  # noqa
    ...


@ta.overload
def repeat(min: int, max: int | None, child: Op) -> Repeat:  # noqa
    ...


def repeat(*args):
    min: int  # noqa
    max: int | None  # noqa

    if len(args) < 2:
        [child] = args
        min, max = 0, None  # noqa

    elif len(args) > 2:
        min, max, child = args  # noqa

    else:
        ti, child = args  # noqa

        if isinstance(ti, Repeat.Times):
            min, max = ti.min, ti.max  # noqa

        else:
            min, max = ti, None  # noqa

    return Repeat(
        Repeat.Times(
            check.isinstance(min, int),
            check.isinstance(max, (int, None)),
        ),
        check.isinstance(child, Op),
    )


ZERO_OR_ONE_TIMES = Repeat.Times(0, 1)


def option(child: Op) -> Repeat:
    return Repeat(ZERO_OR_ONE_TIMES, check.isinstance(child, Op))


##


@ta.final
class Either(Op, lang.Final):
    def __init__(self, *children: Op, first_match: bool = False) -> None:
        super().__init__()

        for c in check.not_empty(children):
            check.isinstance(c, Op)
        self._children = children
        self._first_match = first_match

    @property
    def children(self) -> ta.Sequence[Op]:
        return self._children

    @property
    def first_match(self) -> bool:
        return self._first_match

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}@{id(self):x}('
            f'{", ".join(map(repr, self._children))}'
            f'{", first_match=True" if self._first_match else ""})'
        )


either = Either


##


@ta.final
class RuleRef(Op, lang.Final):
    def __init__(self, name: str) -> None:
        super().__init__()

        self._name = check.non_empty_str(name)
        self._name_f = name.casefold()

    @property
    def name(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._name!r})'

    def _match_repr(self) -> str:
        return repr(self)


rule = RuleRef
