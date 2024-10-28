import heapq
import typing as ta

from omlish import lang
from omlish.testing import pytest as ptu

from ..vectors import Similarity
from ..vectors import Vector
from ..vectors import VectorHit
from ..vectors import VectorHits
from ..vectors import VectorIndexed
from ..vectors import VectorSearch
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
        self._docs: list[VectorIndexed] = []

    def index(self, doc: VectorIndexed) -> None:
        self._docs.append(doc)

    def search(
            self,
            search: VectorSearch,
            *,
            similarity: Similarity | None = None,  # FIXME
    ) -> VectorHits:
        nsv = l2_norm(search.vec)
        h: list[tuple[float, int]] = []
        for i, doc in enumerate(self._docs):
            score = np.dot(nsv, l2_norm(doc.vec))
            heapq.heappush(h, (score, i))
            while len(h) > search.k:
                heapq.heappop(h)
        return VectorHits([
            VectorHit(self._docs[i], score)
            for score, i in reversed(h)
        ])


@ptu.skip.if_cant_import('numpy')
def test_vectors():
    store = SimpleVectorStore()

    for doc in [
        VectorIndexed('foo', Vector([1., 0., 0.])),
        VectorIndexed('foo2', Vector([.9, .1, 0.])),
        VectorIndexed('bar', Vector([0., 1., 0.])),
        VectorIndexed('bar', Vector([.1, .9, 0.])),
        VectorIndexed('baz', Vector([1., 1., 0.])),
    ]:
        store.index(doc)

    print(store.search(VectorSearch(Vector([.9, 0., 0.]), k=2)))
