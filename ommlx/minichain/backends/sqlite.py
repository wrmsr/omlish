import sqlite3
import struct
import typing as ta

from ..vectors import CALC_SIMILARITIES_FUNCS
from ..vectors import Hit
from ..vectors import Hits
from ..vectors import Indexed
from ..vectors import Search
from ..vectors.stores import VectorStore


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

    def index(self, doc: Indexed) -> None:
        self._db.execute(
            f'insert into {self._table_name} (v, vec) values (?, ?)',
            (doc.v, _encode_floats(doc.vec.v)),
        )

    def search(self, search: Search) -> Hits:
        sfn = CALC_SIMILARITIES_FUNCS[search.similarity]

        def calc_score(binary):
            vec = _decode_floats(binary)
            return sfn()

        self._db.create_function('calc_score', 1, calc_score)

        rows = self._db.execute(
            f'select v, calc_score(vec) as score from {self._table_name} order by score desc limit {search.k}',
        )

        ret = []
        for row in rows:
            ret.append(Hit(row[1], row[0]))
        return Hits(ret)
