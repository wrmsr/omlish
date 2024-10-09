import heapq
import typing as ta

from omlish import lang
from omlish.testing import pytest as ptu

from ..vectors import Hit
from ..vectors import Hits
from ..vectors import Indexed
from ..vectors import Search
from ..vectors import Vector
from ..vectors import VectorStore


if ta.TYPE_CHECKING:
    import numpy as np
else:
    np = lang.proxy_import('numpy')


def l2_norm(v: ta.Sequence[float]) -> ta.Sequence[float]:
    d = np.linalg.norm(v)
    if not d:
        return v
    return v / d  # type: ignore


class SimpleVectorStore(VectorStore):
    def __init__(self) -> None:
        super().__init__()
        self._docs: list[Indexed] = []

    def index(self, doc: Indexed) -> None:
        self._docs.append(doc)

    def search(self, search: Search) -> Hits:
        nsv = l2_norm(search.vec)
        h: list[tuple[float, int]] = []
        for i, doc in enumerate(self._docs):
            score = np.dot(nsv, l2_norm(doc.vec))
            heapq.heappush(h, (score, i))
            while len(h) > search.k:
                heapq.heappop(h)
        return Hits([
            Hit(self._docs[i], score)
            for score, i in reversed(h)
        ])


@ptu.skip.if_cant_import('numpy')
def test_vectors():
    store = SimpleVectorStore()

    for doc in [
        Indexed('foo', Vector([1., 0., 0.])),
        Indexed('foo2', Vector([.9, .1, 0.])),
        Indexed('bar', Vector([0., 1., 0.])),
        Indexed('bar', Vector([.1, .9, 0.])),
        Indexed('baz', Vector([1., 1., 0.])),
    ]:
        store.index(doc)

    print(store.search(Search(Vector([.9, 0., 0.]), k=2)))
