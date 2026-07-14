import typing as ta

from ... import lang
from .items import Edge
from .items import Graph
from .items import Node


T = ta.TypeVar('T')


##


def make_simple(graph: ta.Mapping[T, ta.Iterable[T]]) -> Graph:
    return Graph([
        *[Node(n) for n in {*graph, *lang.flatten(graph.values())}],
        *[Edge(k, v) for k, vs in graph.items() for v in vs],
    ])
