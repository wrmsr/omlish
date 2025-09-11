import dataclasses as dc
import typing as ta

from omlish.lite.dataclasses import dataclass_cache_hash


##


@ta.final
@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Node:
    name: str
    children: tuple['Node', ...] | None = None


@ta.final
@dataclass_cache_hash()
@dc.dataclass(frozen=True)
class Match:
    start: int
    nodes: tuple[Node, ...]


Matches: ta.TypeAlias = frozenset[Match]


##


def _main() -> None:
    hash(Node('abc', (Node('def'),)))


if __name__ == '__main__':
    _main()
