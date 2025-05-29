import sqlite3

from omlish.testing import pytest as ptu

from ...vectors.index import VectorIndexed
from ...vectors.search import VectorSearch
from ...vectors.similarity import Similarity
from ...vectors.types import Vector
from ..sqlite import SqliteVectorStore


@ptu.skip.if_cant_import('numpy')
def test_sqlite():
    db = sqlite3.connect(':memory:')
    store = SqliteVectorStore(db, 'foo')  # noqa

    store.index(VectorIndexed(0, Vector([0., 0., 1.])))
    store.index(VectorIndexed(1, Vector([0., 1., 0.])))
    store.index(VectorIndexed(2, Vector([1., 0., 0.])))

    for sim in Similarity:
        hits = store.search(VectorSearch(Vector([0., .1, 0.])), similarity=sim)
        print(hits)
