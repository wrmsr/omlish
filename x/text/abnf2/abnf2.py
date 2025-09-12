import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


@ta.final
class Match(ta.NamedTuple):
    parser: 'Parser'
    start: int
    end: int
    children: tuple['Match', ...]

    # noinspection PyProtectedMember
    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}('
            f'{self.parser._match_repr()}, '
            f'{self.start}, {self.end}'
            f'{f", {self.children!r}" if self.children else ""})'
        )


class Context(lang.Final):
    def __init__(self, source: str) -> None:
        super().__init__()

        self._source = source

    @property
    def source(self) -> str:
        return self._source

    # noinspection PyProtectedMember
    def parse(self, parser: 'Parser', start: int) -> ta.Iterator[Match]:
        return parser._parse(self, start)


class Parser(lang.Abstract, lang.Sealed):
    def _match_repr(self) -> str:
        return f'{self.__class__.__name__}@{id(self)}'

    @abc.abstractmethod
    def _parse(self, ctx: Context, start: int) -> ta.Iterator[Match]:
        raise NotImplementedError


##


class Literal(Parser, lang.Abstract):
    def _match_repr(self) -> str:
        return repr(self)


class StringLiteral(Literal):
    def __init__(self, value: str) -> None:
        super().__init__()

        self._value = value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._value!r})'

    # noinspection PyProtectedMember
    def _parse(self, ctx: Context, start: int) -> ta.Iterator[Match]:
        if start < len(ctx._source):
            source = ctx._source[start : start + len(self._value)]
            if source == self._value:
                yield Match(self, start, start + len(source), ())


class CaseInsensitiveStringLiteral(Literal):
    def __init__(self, value: str) -> None:
        super().__init__()

        self._value = value.casefold()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._value!r})'

    # noinspection PyProtectedMember
    def _parse(self, ctx: Context, start: int) -> ta.Iterator[Match]:
        if start < len(ctx._source):
            source = ctx._source[start : start + len(self._value)].casefold()
            if source == self._value:
                yield Match(self, start, start + len(source), ())


class RangeLiteral(Literal):
    class Range(ta.NamedTuple):
        lo: str
        hi: str

    def __init__(self, value: Range) -> None:
        super().__init__()

        self._value = value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._value!r})'

    # noinspection PyProtectedMember
    def _parse(self, ctx: Context, start: int) -> ta.Iterator[Match]:
        try:
            source = ctx._source[start]
        except IndexError:
            return
        # ranges are always case-sensitive
        if (value := self._value).lo <= source <= value.hi:
            yield Match(self, start, start + 1, ())


##


class Concat(Parser):
    def __init__(self, *children: Parser) -> None:
        super().__init__()

        self._children = children

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({", ".join(map(repr, self._children))})'

    def _parse(self, ctx: Context, start: int) -> ta.Iterator[Match]:
        i = 0
        match_tups: list[tuple[Match, ...]] = [()]
        for cur in self._children:
            next_match_tups: list[tuple[Match, ...]] = []
            for mt in match_tups:
                for cm in ctx.parse(cur, mt[-1].end if mt else 0):
                    next_match_tups.append((*mt, cm))
                    i += 1
            if not next_match_tups:
                return
            match_tups = next_match_tups
        if not i:
            return
        for mt in sorted(match_tups, key=len, reverse=True):
            yield Match(self, start, mt[-1].end, mt)


##


class Repeat(Parser):
    @dc.dataclass(frozen=True)
    class Times:
        min: int
        max: int | None = None

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}({self.min}{f", {self.max!r}" if self.max is not None else ""})'

    def __init__(self, times: Times, child: Parser) -> None:
        super().__init__()

        self._times = times
        self._child = child

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._times}, {self._child!r})'

    def _parse(self, ctx: Context, start: int) -> ta.Iterator[Match]:
        match_tup_set: set[tuple[Match, ...]] = set()
        last_match_tup_set: set[tuple[Match, ...]] = {()}
        i = 0
        while True:
            if self._times.max is not None and i == self._times.max:
                break
            next_match_tup_set: set[tuple[Match, ...]] = set()
            for mt in last_match_tup_set:
                for cm in ctx.parse(self._child, mt[-1].end if mt else start):
                    next_match_tup_set.add((*mt, cm))
            if next_match_tup_set < match_tup_set:
                break
            i += 1
            match_tup_set |= next_match_tup_set
            last_match_tup_set = next_match_tup_set
        if i < self._times.min:
            return
        for mt in sorted(match_tup_set, key=len, reverse=True):
            yield Match(self, start, mt[-1].end, mt)  # noqa


##


def _main() -> None:
    def parse(p: Parser, s: str) -> list[Match]:
        return list(Context(s).parse(p, 0))

    print(parse(Concat(StringLiteral('foo'), StringLiteral('bar')), 'foobar'))
    print(parse(Repeat(Repeat.Times(3), StringLiteral('ab')), 'ababab'))


if __name__ == '__main__':
    _main()
