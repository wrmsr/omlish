import pprint
import typing as ta

import numpy as np
import sklearn.neighbors


Embedding: ta.TypeAlias = ta.Sequence[float]


class VecStore:
    def __init__(
            self,
            embed: ta.Callable[[ta.Any], Embedding],
    ) -> None:
        super().__init__()
        self._embed = embed

        self._neighbors = sklearn.neighbors.NearestNeighbors(metric='minkowski')

        self._embeddings: list[Embedding] = []
        self._items: list[ta.Any] = []

        self._embeddings_np: ta.Any = np.asarray([])

    def _compute(self) -> None:
        self._embeddings_np = np.asarray(self._embeddings)
        self._neighbors.fit(self._embeddings_np)

    def add_items(self, items: ta.Iterable[ta.Any]) -> None:
        items = list(items)
        self._items.extend(items)
        self._embeddings.extend(map(self._embed, items))
        self._compute()

    def search(self, query: ta.Any, k: int = 1) -> list[tuple[ta.Any, float]]:
        query_embedding = self._embed(query)
        neigh_dists, neigh_idxs = self._neighbors.kneighbors([query_embedding], n_neighbors=k)
        return [(self._items[idx], dist) for idx, dist in zip(neigh_idxs[0], neigh_dists[0])]


def _main() -> None:
    vs = VecStore(lambda s: [float(len(s))])

    vs.add_items([
        'hi',
        'there',
        'this is dumb',
        'yes',
    ])

    pprint.pprint(vs.search('barf', 3))


if __name__ == '__main__':
    _main()
