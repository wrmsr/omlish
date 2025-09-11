import abc
import dataclasses as dc
import typing as ta

from omlish import lang
from omlish.lite.dataclasses import dataclass_cache_hash


##


@dc.dataclass(frozen=True)
class Node(lang.Abstract, lang.Sealed):
    # @property
    # @abc.abstractmethod
    # def name(self) -> str:
    #     raise NotImplementedError

    pass


@ta.final
@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class ConcatenateNode(Node, lang.Final):
    name: str
    children: tuple['Node', ...] | None = None


@ta.final
@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class LiteralNode(Node, lang.Final):
    start: int
    length: int

    @property
    def name(self) -> str:
        return 'literal'


@ta.final
@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Match(lang.Final):
    start: int
    nodes: tuple[Node, ...]


Matches: ta.TypeAlias = frozenset[Match]


##


@dc.dataclass(frozen=True)
class ParseContext:
    source: str


class Parser(lang.Abstract):
    @abc.abstractmethod
    def parse(self, ctx: ParseContext, start: int) -> Matches:
        raise NotImplementedError


##


class Literal(Parser):
    class Range(ta.NamedTuple):
        lo: int
        hi: int

    def __init__(
            self,
            value:
    ):






##


def _main() -> None:
    hash(Node('abc', (Node('def'),)))


if __name__ == '__main__':
    _main()
