"""
TODO:
 - desugar Literal - StringLiteral, RangeLiteral
"""
import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class Match(lang.Final):
    parser: 'Parser'
    start: int
    length: int
    children: tuple['Match', ...] | None = dc.xfield(None, repr_fn=lang.opt_repr)


@dc.dataclass(frozen=True)
class Context(lang.Final):
    source: str


class Parser(lang.Abstract, lang.Sealed):
    @abc.abstractmethod
    def parse(self, ctx: Context, start: int) -> ta.Iterator[Match]:
        raise NotImplementedError


##


class Literal(Parser, lang.Abstract):
    pass


class StringLiteral(Parser):
    def __init__(self, value: str) -> None:
        super().__init__()

        self._value = value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._value!r})'

    def parse(self, ctx: Context, start: int) -> ta.Iterator[Match]:
        if start < len(ctx.source):
            source = ctx.source[start : start + len(self._value)]
            if source == self._value:
                yield Match(self, start, len(source))


class CaseInsensitiveStringLiteral(Literal):
    def __init__(self, value: str) -> None:
        super().__init__()

        self._value = value.casefold()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._value!r})'

    def parse(self, ctx: Context, start: int) -> ta.Iterator[Match]:
        if start < len(ctx.source):
            source = ctx.source[start : start + len(self._value)].casefold()
            if source == self._value:
                yield Match(self, start, len(source))


class RangeLiteral(Literal):
    class Range(ta.NamedTuple):
        lo: str
        hi: str

    def __init__(self, value: Range) -> None:
        super().__init__()

        self._value = value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._value!r})'

    def parse(self, ctx: Context, start: int) -> ta.Iterator[Match]:
        try:
            source = ctx.source[start]
        except IndexError:
            return

        if (value := self._value).lo <= source <= value.hi:
            yield Match(self, start, 1)


##


def _main() -> None:
    ctx = Context('foo')
    parser = StringLiteral('foo')
    print(list(parser.parse(ctx, 0)))


if __name__ == '__main__':
    _main()
