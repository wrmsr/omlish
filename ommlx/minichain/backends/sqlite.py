"""
TODO:
 - udf name manager - acquire leases to unique names, release back to pool, replace with dummy
"""
import sqlite3

from omlish import lang

from ..vectors.index import VectorIndexed
from ..vectors.search import VectorHit
from ..vectors.search import VectorHits
from ..vectors.search import VectorSearch
from ..vectors.similarity import CALC_NP_SIMILARITIES_FUNCS
from ..vectors.similarity import Similarity
from ..vectors.stores import VectorStore
from ..vectors.vectors import Vector


##


class SqliteVectorStore(VectorStore):
    def __init__(
            self,
            db: sqlite3.Connection,
            table_name: str,
    ) -> None:
        super().__init__()

        self._db = db
        self._table_name = table_name

        db.execute(''.join([
            f'create table if not exists {self._table_name} (',
            ', ' .join([
                'v integer primary key',
                f'vec blob',
            ]),
            ')',
        ]))

    def index(self, doc: VectorIndexed) -> None:
        self._db.execute(
            f'insert into {self._table_name} (v, vec) values (?, ?)',  # noqa
            (doc.v, doc.vec.bytes()),
        )

    def search(
            self,
            search: VectorSearch,
            *,
            similarity: Similarity | None = None,
    ) -> VectorHits:
        snp = search.vec.np()
        npfn = CALC_NP_SIMILARITIES_FUNCS[similarity or Similarity.DOT]

        def calc_score(binary):
            rnp = Vector(binary).np()
            score = float(npfn(rnp.reshape(1, -1), snp)[0])
            return score

        udf_name = 'calc_score'
        self._db.create_function(udf_name, 1, calc_score)
        try:
            rows = self._db.execute(
                f'select v, calc_score(vec) as score '  # noqa
                f'from {self._table_name} '
                f'order by score desc '
                f'limit {search.k}',
            )

            ret = []
            for row in rows:
                ret.append(VectorHit(row[0], row[1]))
            return VectorHits(ret)

        finally:
            self._db.create_function(udf_name, 0, lang.void)
