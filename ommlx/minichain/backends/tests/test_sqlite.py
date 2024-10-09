import sqlite3

from ...vectors import Indexed
from ...vectors import Search
from ...vectors import Vector
from ..sqlite import SqliteVectorStore


def test_sqlite():
    db = sqlite3.connect(':memory:')
    store = SqliteVectorStore(db, 'foo')  # noqa

    store.index(Indexed(0, Vector([0., 0., 1.])))
    store.index(Indexed(1, Vector([0., 1., 0.])))
    store.index(Indexed(2, Vector([1., 0., 0.])))

    hits = store.search(Search(Vector([0., .1, 0.])))
    print(hits)
