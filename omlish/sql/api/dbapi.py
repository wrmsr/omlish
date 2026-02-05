import contextlib
import typing as ta

from ... import check
from ...resources import SimpleResource
from ..dbapi import abc as dbapi_abc
from ..params import ParamStyle
from . import querierfuncs as qf
from .adapters import Adapter
from .columns import Column
from .columns import Columns
from .core import Conn
from .core import Db
from .core import Rows
from .core import Transaction
from .queries import Query
from .queries import Queryable
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


#


class DbapiRows(Rows):
    def __init__(
            self,
            cursor: dbapi_abc.DbapiCursor,
            columns: Columns,
    ) -> None:
        super().__init__()

        self._cursor = cursor
        self._columns = columns

    @property
    def columns(self) -> Columns:
        return self._columns

    def __next__(self) -> Row:
        values = self._cursor.fetchone()
        if values is None:
            raise StopIteration
        return Row(self._columns, values)


#


class DbapiTransaction(Transaction, SimpleResource):
    def __init__(self, conn: 'DbapiConn') -> None:
        super().__init__()

        self._conn = conn

    _state: ta.Literal['new', 'open', 'committed', 'aborted'] = 'new'

    def _enter(self) -> None:
        check.state(self._state == 'new')
        qf.exec(self._conn, 'begin')
        self._state = 'open'

    def _commit_internal(self) -> None:
        check.state(self._state == 'open')
        qf.exec(self._conn, 'commit')
        self._state = 'committed'

    def _rollback_internal(self) -> None:
        check.state(self._state == 'open')
        qf.exec(self._conn, 'rollback')
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

    def query(self, query: Queryable) -> ta.ContextManager[Rows]:
        self._check_entered()
        check.state(self._state == 'open')
        return self._conn.query(query)

    def commit(self) -> None:
        self._check_entered()
        self._commit_internal()

    def rollback(self) -> None:
        self._check_entered()
        self._rollback_internal()


#


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
            adapter = DbapiAdapter()
        self._adapter = adapter

        if not self._conn.autocommit:
            self._conn.autocommit = True
        check.state(bool(self._conn.autocommit))

    @property
    def adapter(self) -> Adapter:
        return self._adapter

    def _query(self, es: contextlib.ExitStack, query: Queryable) -> DbapiRows:
        query = check.isinstance(query, Query)

        cursor = self._conn.cursor()
        es.enter_context(contextlib.closing(cursor))

        cursor.execute(query.text, *query.args)
        columns = build_dbapi_columns(cursor.description)

        return DbapiRows(cursor, columns)

    def query(self, query: Queryable) -> ta.ContextManager[Rows]:
        @contextlib.contextmanager
        def inner():
            with contextlib.ExitStack() as es:
                yield self._query(es, query)

        return inner()

    def begin(self) -> ta.ContextManager[Transaction]:
        return DbapiTransaction(self)


#


class DbapiDb(Db):
    def __init__(
            self,
            connector: ta.Callable[[], ta.ContextManager[dbapi_abc.DbapiConnection]],
            *,
            adapter: ta.Optional['DbapiAdapter'] = None,
            param_style: ParamStyle | None = None,
    ) -> None:
        super().__init__()

        self._connector = connector
        if adapter is None:
            adapter = DbapiAdapter(
                param_style=param_style,
            )
        else:
            check.none(param_style)
        self._adapter = adapter

    @property
    def adapter(self) -> Adapter:
        return self._adapter

    def _connect(self, es: contextlib.ExitStack) -> DbapiConn:
        return DbapiConn(es.enter_context(self._connector()), adapter=self._adapter)

    def connect(self) -> ta.ContextManager[Conn]:
        @contextlib.contextmanager
        def inner():
            with contextlib.ExitStack() as es:
                yield self._connect(es)

        return inner()

    def query(self, query: Queryable) -> ta.ContextManager[Rows]:
        @contextlib.contextmanager
        def inner():
            with contextlib.ExitStack() as es:
                yield self._connect(es)._query(es, query)  # noqa

        return inner()


#


class DbapiAdapter(Adapter):
    def __init__(
            self,
            *,
            param_style: ParamStyle | None = None,
    ) -> None:
        super().__init__()

        self._param_style = param_style

    @property
    def param_style(self) -> ParamStyle | None:
        return self._param_style

    def scan_type(self, c: Column) -> type:
        raise NotImplementedError
