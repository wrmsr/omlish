import typing as ta

import sqlalchemy as sa

from ... import check
from ...resources import SimpleResource
from .. import api
from ..api.dbapi import build_dbapi_columns


T = ta.TypeVar('T')


##


class SqlalchemyApiWrapper(SimpleResource, ta.Generic[T]):
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

    def _close(self, reason: BaseException | None) -> None:
        if self._auto_close and hasattr(self._u, 'close'):
            self._u.close()

        super()._close(reason)


##


class SqlalchemyApiRows(SimpleResource, api.Rows):
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


class SqlalchemyTransaction(SimpleResource, api.Transaction):
    @property
    def adapter(self) -> api.Adapter:
        return DEFAULT_SQLALCHEMY_ADAPTER

    def query(self, query: api.Query) -> ta.ContextManager[api.Rows]:
        raise NotImplementedError

    def commit(self) -> None:
        raise NotImplementedError

    def rollback(self) -> None:
        raise NotImplementedError


class SqlalchemyApiConn(SqlalchemyApiWrapper[sa.engine.Connection], api.Conn):
    @property
    def adapter(self) -> api.Adapter:
        return DEFAULT_SQLALCHEMY_ADAPTER

    def query(self, query: api.Query) -> ta.ContextManager[api.Rows]:
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

    def begin(self) -> ta.ContextManager[api.Transaction]:
        raise NotImplementedError


class SqlalchemyApiDb(SqlalchemyApiWrapper[sa.engine.Engine], api.Db):
    def connect(self) -> ta.ContextManager[api.Conn]:
        return SqlalchemyApiConn(self._u.connect(), auto_close=True)

    @property
    def adapter(self) -> api.Adapter:
        return DEFAULT_SQLALCHEMY_ADAPTER

    def query(self, query: api.Query) -> ta.ContextManager[api.Rows]:
        with self.connect() as conn:
            return conn.query(query)


class SqlalchemyApiAdapter(api.Adapter):
    def scan_type(self, c: api.Column) -> type:
        raise NotImplementedError


DEFAULT_SQLALCHEMY_ADAPTER = SqlalchemyApiAdapter()


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
