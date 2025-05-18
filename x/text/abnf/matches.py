import typing as ta


if ta.TYPE_CHECKING:
    from .nodes import Nodes


##


class Match:
    def __init__(self, nodes: 'Nodes', start: int) -> None:
        super().__init__()

        self.nodes = nodes
        self.start = start

    def __hash__(self) -> int:
        value = ''.join(n.value for n in self.nodes)
        return hash((value, self.start))

    def __str__(self) -> str:
        return f'Match({"".join(n.value for n in self.nodes)}, {self.start})'

    def __eq__(self, /, o: object) -> bool:
        return isinstance(o, self.__class__) and hash(self) == hash(o)


MatchSet: ta.TypeAlias = set[Match]
Matches: ta.TypeAlias = ta.Iterator[Match]


#


def sorted_by_longest_match(matches: ta.Iterable[Match]) -> list[Match]:
    return sorted(matches, key=lambda item: item.start, reverse=True)


def next_longest_match(matches: MatchSet) -> ta.Generator[Match, None, None]:
    yield from sorted_by_longest_match(list(matches))
