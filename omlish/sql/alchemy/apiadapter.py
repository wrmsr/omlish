import typing as ta

import sqlalchemy as sa

from ... import check
from .. import api
from ..api.dbapi import build_dbapi_columns


T = ta.TypeVar('T')


##


class SqlalchemyApiWrapper(api.ContextCloser, ta.Generic[T]):
    def __init__(
            self,
            u: T,
            *,
            auto_close: bool = False,
    ) -> None:
        super().__init__()

        self._u = u
        self._auto_close = auto_close

    @property
    @ta.override
    def _is_resourceless(self) -> bool:
        return not self._auto_close

    def _close(self) -> None:
        if self._auto_close and hasattr(self._u, 'close'):
            self._u.close()

        super()._close()


##


class SqlalchemyApiRows(api.Rows):
    def __init__(self, columns: api.Columns, rows: ta.Sequence[api.Row]) -> None:
        super().__init__()

        self._columns = columns
        self._rows = rows

        self._it = iter(self._rows)

    @property
    def columns(self) -> api.Columns:
        return self._columns

    def __next__(self) -> api.Row:
        return next(self._it)


class SqlalchemyApiConn(SqlalchemyApiWrapper[sa.engine.Connection], api.Conn):
    @property
    def adapter(self) -> api.Adapter:
        raise NotImplementedError

    def query(self, query: api.Query) -> api.Rows:
        check.empty(query.args)
        result: sa.engine.cursor.CursorResult
        with self._u.execute(sa.text(query.text)) as result:
            cols = build_dbapi_columns(result.cursor.description)
            sa_rows = result.fetchall()
            rows = [
                api.Row(cols, tuple(sa_row))
                for sa_row in sa_rows
            ]
        return SqlalchemyApiRows(cols, rows)


class SqlalchemyApiDb(SqlalchemyApiWrapper[sa.engine.Engine], api.Db):
    def connect(self) -> api.Conn:
        return SqlalchemyApiConn(self._u.connect(), auto_close=True)

    @property
    def adapter(self) -> api.Adapter:
        raise NotImplementedError


class SqlalchemyApiAdapter(api.Adapter):
    def scan_type(self, c: api.Column) -> type:
        raise NotImplementedError


##


@ta.overload
def api_adapt(o: sa.engine.Connection) -> SqlalchemyApiConn:
    ...


@ta.overload
def api_adapt(o: api.Conn) -> api.Conn:
    ...


@ta.overload
def api_adapt(o: sa.engine.Engine) -> SqlalchemyApiDb:
    ...


@ta.overload
def api_adapt(o: api.Db) -> api.Db:
    ...


def api_adapt(o):
    if isinstance(o, sa.engine.Connection):
        return SqlalchemyApiConn(o)
    elif isinstance(o, api.Conn):
        return o

    elif isinstance(o, sa.engine.Engine):
        return SqlalchemyApiDb(o)
    elif isinstance(o, api.Db):
        return o

    else:
        raise TypeError(o)
