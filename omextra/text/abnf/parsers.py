import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang

from .base import Match
from .base import Parser
from .base import _Context


##


class Literal(Parser, lang.Abstract):
    def _match_repr(self) -> str:
        return repr(self)


class StringLiteral(Literal):
    def __init__(self, value: str) -> None:
        super().__init__()

        self._value = check.non_empty_str(value)

    @property
    def value(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._value!r})'

    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        if start < len(ctx._source):  # noqa
            source = ctx._source[start : start + len(self._value)]  # noqa
            if source == self._value:
                yield Match(self, start, start + len(source), ())


class CaseInsensitiveStringLiteral(Literal):
    def __init__(self, value: str) -> None:
        super().__init__()

        self._value = check.non_empty_str(value).casefold()

    @property
    def value(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._value!r})'

    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        if start < len(ctx._source):  # noqa
            source = ctx._source[start : start + len(self._value)].casefold()  # noqa
            if source == self._value:
                yield Match(self, start, start + len(source), ())


class RangeLiteral(Literal):
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

    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        try:
            source = ctx._source[start]  # noqa
        except IndexError:
            return
        # ranges are always case-sensitive
        if (value := self._value).lo <= source <= value.hi:
            yield Match(self, start, start + 1, ())


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


class Concat(Parser):
    def __init__(self, *children: Parser) -> None:
        super().__init__()

        for c in check.not_empty(children):
            check.isinstance(c, Parser)
        self._children = children

    @property
    def children(self) -> ta.Sequence[Parser]:
        return self._children

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({", ".join(map(repr, self._children))})'

    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        i = 0
        match_tups: list[tuple[Match, ...]] = [()]
        for cp in self._children:
            next_match_tups: list[tuple[Match, ...]] = []
            for mt in match_tups:
                for cm in ctx.iter_parse(cp, mt[-1].end if mt else start):
                    next_match_tups.append((*mt, cm))
                    i += 1
            if not next_match_tups:
                return
            match_tups = next_match_tups
        if not i:
            return
        for mt in sorted(match_tups, key=len, reverse=True):
            yield Match(self, start, mt[-1].end if mt else start, mt)


concat = Concat


##


class Repeat(Parser):
    @dc.dataclass(frozen=True)
    class Times:
        min: int = 0
        max: int | None = None

        def __post_init__(self) -> None:
            if self.max is not None:
                check.state(self.max >= self.min)

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}({self.min}{f", {self.max!r}" if self.max is not None else ""})'

    def __init__(self, times: Times, child: Parser) -> None:
        super().__init__()

        self._times = check.isinstance(times, Repeat.Times)
        self._child = check.isinstance(child, Parser)

    @property
    def times(self) -> Times:
        return self._times

    @property
    def child(self) -> Parser:
        return self._child

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._times}, {self._child!r})'

    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        match_tup_set: set[tuple[Match, ...]] = set()
        last_match_tup_set: set[tuple[Match, ...]] = {()}
        i = 0
        while True:
            if self._times.max is not None and i == self._times.max:
                break
            next_match_tup_set: set[tuple[Match, ...]] = set()
            for mt in last_match_tup_set:
                for cm in ctx.iter_parse(self._child, mt[-1].end if mt else start):
                    next_match_tup_set.add((*mt, cm))
            if not next_match_tup_set or next_match_tup_set < match_tup_set:
                break
            i += 1
            match_tup_set |= next_match_tup_set
            last_match_tup_set = next_match_tup_set
        if i < self._times.min:
            return
        for mt in sorted(match_tup_set or [()], key=len, reverse=True):
            yield Match(self, start, mt[-1].end if mt else start, mt)  # noqa


class Option(Repeat):
    def __init__(self, child: Parser) -> None:
        super().__init__(Repeat.Times(0, 1), child)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._child!r})'


option = Option


@ta.overload
def repeat(child: Parser) -> Repeat:  # noqa
    ...


@ta.overload
def repeat(times: Repeat.Times, child: Parser) -> Repeat:  # noqa
    ...


@ta.overload
def repeat(min: int, child: Parser) -> Repeat:  # noqa
    ...


@ta.overload
def repeat(min: int, max: int | None, child: Parser) -> Repeat:  # noqa
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

    if (min, max) == (0, 1):
        return Option(check.isinstance(child, Parser))

    else:
        return Repeat(
            Repeat.Times(
                check.isinstance(min, int),
                check.isinstance(max, (int, None)),
            ),
            check.isinstance(child, Parser),
        )


##


class Either(Parser):
    def __init__(self, *children: Parser, first_match: bool = False) -> None:
        super().__init__()

        for c in check.not_empty(children):
            check.isinstance(c, Parser)
        self._children = children
        self._first_match = first_match

    @property
    def children(self) -> ta.Sequence[Parser]:
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

    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        for cp in self._children:
            found = False
            for cm in ctx.iter_parse(cp, start):
                found = True
                yield Match(self, start, cm.end, (cm,))
            if found and self._first_match:
                return


either = Either


##


class RuleRef(Parser):
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

    def _iter_parse(self, ctx: _Context, start: int) -> ta.Iterator[Match]:
        cp = ctx._grammar._rules_by_name_f[self._name_f].parser  # noqa
        for cm in ctx.iter_parse(cp, start):
            yield Match(self, cm.start, cm.end, (cm,))


rule = RuleRef
