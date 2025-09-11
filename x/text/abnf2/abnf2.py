import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


@dc.dataclass(frozen=True)
class Node(lang.Abstract, lang.Sealed):
    pass


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class ConcatenateNode(Node, lang.Final):
    parser: 'Parser'
    children: tuple['Node', ...]


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class LiteralNode(Node, lang.Final):
    parser: 'Literal'
    start: int
    length: int


@dc.dataclass(frozen=True)
@dc.extra_class_params(cache_hash=True)
class Match(lang.Final):
    start: int
    nodes: tuple[Node, ...]


##


@dc.dataclass(frozen=True)
class Context:
    source: str


class Parser(lang.Abstract):
    @abc.abstractmethod
    def parse(self, ctx: Context, start: int) -> ta.Iterator[Match]:
        raise NotImplementedError


##


class Literal(Parser, lang.Final):
    class Range(ta.NamedTuple):
        lo: str
        hi: str

    def __init__(
            self,
            value: str | Range,
            *,
            case_insensitive: bool | None = None,
    ) -> None:
        super().__init__()

        if isinstance(value, str):
            if case_insensitive:
                value = value.casefold()
        elif case_insensitive is not None:
            raise TypeError('Should not set case_insensitive with non-string literal')
        self._value = value
        self._case_insensitive = case_insensitive

    def parse(self, ctx: Context, start: int) -> ta.Iterator[Match]:
        if not isinstance(value := self._value, str):
            try:
                source = ctx.source[start]
            except IndexError:
                return

            # ranges are always case-sensitive
            if value.lo <= source <= value.hi:
                yield Match(start, (LiteralNode(self, start, 1),))

        else:
            if start < len(ctx.source):
                source = ctx.source[start : start + len(self._value)]
                if self._case_insensitive:
                    source = source.casefold()
                if source == value:
                    yield Match(start, (LiteralNode(self, start, len(source)),))


##


def _main() -> None:
    ctx = Context('foo')
    parser = Literal('foo')
    print(list(parser.parse(ctx, 0)))


if __name__ == '__main__':
    _main()
