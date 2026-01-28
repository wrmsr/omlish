import typing as ta

from ... import check
from ..dbapi import abc as dbapi_abc
from . import funcs
from .base import Adapter
from .base import Conn
from .base import Db
from .base import Rows
from .base import Transaction
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

    def _close(self, reason: BaseException | None) -> None:
        self._cursor.close()

        super()._close(reason)

    @property
    def columns(self) -> Columns:
        return self._columns

    def __next__(self) -> Row:
        self._check_entered()
        values = self._cursor.fetchone()
        if values is None:
            raise StopIteration
        return Row(self._columns, values)


class DbapiTransaction(Transaction):
    def __init__(self, conn: 'DbapiConn') -> None:
        super().__init__()

        self._conn = conn

    _state: ta.Literal['new', 'open', 'committed', 'aborted'] = 'new'

    def _enter(self) -> None:
        check.state(self._state == 'new')
        funcs.exec(self._conn, 'begin')
        self._state = 'open'

    def _commit_internal(self) -> None:
        check.state(self._state == 'open')
        funcs.exec(self._conn, 'commit')
        self._state = 'committed'

    def _rollback_internal(self) -> None:
        check.state(self._state == 'open')
        funcs.exec(self._conn, 'rollback')
        self._state = 'aborted'

    def _close(self, reason: BaseException | None) -> None:
        if self._state == 'open':
            if reason is not None:
                self._rollback_internal()
            else:
                self._commit_internal()

        super()._close(reason)

    @property
    def adapter(self) -> Adapter:
        return self._conn.adapter

    def query(self, query: Query) -> Rows:
        self._check_entered()
        check.state(self._state == 'open')
        return self._conn.query(query)

    def commit(self) -> None:
        self._check_entered()
        self._commit_internal()

    def rollback(self) -> None:
        self._check_entered()
        self._rollback_internal()


class DbapiConn(Conn):
    def __init__(
            self,
            conn: dbapi_abc.DbapiConnection,
            *,
            adapter: ta.Optional['DbapiAdapter'] = None,
    ) -> None:
        super().__init__()

        self._conn = conn
        if adapter is None:
            adapter = DEFAULT_DBAPI_ADAPTER
        self._adapter = adapter

    def _enter(self) -> None:
        super()._enter()

        if not self._conn.autocommit:
            self._conn.autocommit = True
        check.state(bool(self._conn.autocommit))

    def _close(self, reason: BaseException | None) -> None:
        self._conn.close()

        super()._close(reason)

    @property
    def adapter(self) -> Adapter:
        return self._adapter

    def query(self, query: Query) -> Rows:
        self._check_entered()
        cursor = self._conn.cursor()
        try:
            cursor.execute(query.text)
            columns = build_dbapi_columns(cursor.description)
            return DbapiRows(cursor, columns)

        except Exception as e:  # noqa
            cursor.close()
            raise

    def begin(self) -> Transaction:
        return DbapiTransaction(self)


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
            adapter = DEFAULT_DBAPI_ADAPTER
        self._adapter = adapter

    @property
    def adapter(self) -> Adapter:
        return self._adapter

    def connect(self) -> Conn:
        self._check_entered()
        dbapi_conn = self._conn_fac()
        return DbapiConn(dbapi_conn)

    def query(self, query: Query) -> Rows:
        # with self.connect() as conn:
        #     return conn.query(query)
        # FIXME: need minichain-style Resource group? can't close conn with live Rows
        raise NotImplementedError


class DbapiAdapter(Adapter):
    def scan_type(self, c: Column) -> type:
        raise NotImplementedError


DEFAULT_DBAPI_ADAPTER = DbapiAdapter()
