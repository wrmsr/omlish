import typing as ta

from ... import check
from .. import abc as dbapi_abc
from .base import Adapter
from .base import Conn
from .base import Db
from .base import Rows
from .columns import Column
from .columns import Columns
from .queries import Query
from .rows import Row


##


def build_dbapi_columns(desc: ta.Sequence[dbapi_abc.DbapiColumnDescription] | None) -> Columns:
    if desc is None:
        return Columns.empty()

    cols: list[Column] = []
    for desc_col in desc:
        dbapi_col = dbapi_abc.DbapiColumnDescription_.of(desc_col)

        cols.append(Column(
            check.non_empty_str(dbapi_col.name),
        ))

    return Columns(*cols)


class DbapiRows(Rows):
    def __init__(
            self,
            cursor: dbapi_abc.DbapiCursor,
            columns: Columns,
    ) -> None:
        super().__init__()

        self._cursor = cursor
        self._columns = columns

    def _close(self) -> None:
        self._cursor.close()

        super()._close()

    @property
    def columns(self) -> Columns:
        return self._columns

    def __next__(self) -> Row:
        self._check_entered()
        values = self._cursor.fetchone()
        if values is None:
            raise StopIteration
        return Row(self._columns, values)


class DbapiConn(Conn):
    def __init__(self, conn: dbapi_abc.DbapiConnection) -> None:
        super().__init__()

        self._conn = conn

    def _close(self) -> None:
        self._conn.close()

        super()._close()

    @property
    def adapter(self) -> Adapter:
        raise NotImplementedError

    def query(self, query: Query) -> Rows:
        self._check_entered()
        cursor = self._conn.cursor()
        try:
            cursor.execute(query.text)
            columns = build_dbapi_columns(cursor.description)
            return DbapiRows(cursor, columns)

        except Exception:  # noqa
            cursor.close()
            raise


class DbapiDb(Db):
    def __init__(
            self,
            conn_fac: ta.Callable[[], dbapi_abc.DbapiConnection],
            *,
            adapter: ta.Optional['DbapiAdapter'] = None,
    ) -> None:
        super().__init__()

        self._conn_fac = conn_fac
        if adapter is None:
            adapter = DbapiAdapter()
        self._adapter = adapter

    def connect(self) -> Conn:
        self._check_entered()
        dbapi_conn = self._conn_fac()
        return DbapiConn(dbapi_conn)

    @property
    def adapter(self) -> Adapter:
        return self._adapter


class DbapiAdapter(Adapter):
    def scan_type(self, c: Column) -> type:
        raise NotImplementedError
