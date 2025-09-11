import abc
import dataclasses as dc
import typing as ta

from omlish import lang
from omlish.lite.dataclasses import dataclass_cache_hash


##


@dc.dataclass(frozen=True)
class Node(lang.Abstract, lang.Sealed):
    pass


@ta.final
@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class ConcatenateNode(Node, lang.Final):
    parser: 'Parser'
    children: tuple['Node', ...]


@ta.final
@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class LiteralNode(Node, lang.Final):
    parser: 'Literal'
    start: int
    length: int


@ta.final
@dataclass_cache_hash()
@dc.dataclass(frozen=True)
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


class Literal(Parser, lang.Abstract):
    class Range(ta.NamedTuple):
        lo: int
        hi: int

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
            raise NotImplementedError

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
    print(parser.parse(ctx, 0))


if __name__ == '__main__':
    _main()
