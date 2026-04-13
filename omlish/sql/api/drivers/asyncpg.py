import contextlib
import types
import typing as ta

from .... import check
from ...params import ParamStyle
from ..adapters import Adapter
from ..columns import Column
from ..columns import Columns
from ..core import AsyncConn
from ..core import AsyncDb
from ..core import AsyncRows
from ..core import AsyncTxn
from ..queries import Query
from ..queries import Queryable
from ..rows import Row


if ta.TYPE_CHECKING:
    import asyncpg


##


def build_asyncpg_columns(
        attrs: ta.Sequence[ta.Any] | None,
) -> Columns:
    if attrs is None:
        return Columns.empty()

    cols: list[Column] = []
    for attr in attrs:
        cols.append(Column(
            check.non_empty_str(attr.name),
        ))

    return Columns(*cols)


#


class AsyncpgRows(AsyncRows):
    def __init__(
            self,
            cursor: ta.Any,
            columns: Columns,
    ) -> None:
        super().__init__()

        self._cursor = cursor
        self._columns = columns

    @property
    def columns(self) -> Columns:
        return self._columns

    async def __anext__(self) -> Row:
        rec = await self._cursor.fetchrow()
        if rec is None:
            raise StopAsyncIteration
        return Row(self._columns, tuple(rec))


#


class AsyncpgTxn(AsyncTxn):
    def __init__(
            self,
            conn: AsyncpgConn,
    ) -> None:
        super().__init__()

        self._conn = conn
        self._tr = conn._conn.transaction()  # noqa

    _state: ta.Literal['new', 'open', 'committed', 'aborted'] = 'new'

    async def __aenter__(self) -> ta.Self:
        check.state(self._state == 'new')
        await self._tr.start()
        self._state = 'open'
        return self

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: types.TracebackType | None,
    ) -> None:
        if self._state == 'open':
            if exc is not None:
                await self._rollback_internal()
            else:
                await self._commit_internal()

    def _check_open(self) -> None:
        check.state(self._state == 'open')

    async def _commit_internal(self) -> None:
        self._check_open()
        await self._tr.commit()
        self._state = 'committed'

    async def _rollback_internal(self) -> None:
        self._check_open()
        await self._tr.rollback()
        self._state = 'aborted'

    @property
    def adapter(self) -> Adapter:
        return self._conn.adapter

    def query(self, query: Queryable) -> ta.AsyncContextManager[AsyncRows]:
        self._check_open()

        @contextlib.asynccontextmanager
        async def inner():
            q = check.isinstance(query, Query)

            stmt = await self._conn._conn.prepare(q.text)  # noqa
            columns = build_asyncpg_columns(stmt.get_attributes())
            cursor = await stmt.cursor(*q.args)

            yield AsyncpgRows(cursor, columns)

        return inner()

    async def commit(self) -> None:
        await self._commit_internal()

    async def rollback(self) -> None:
        await self._rollback_internal()


#


class AsyncpgConn(AsyncConn):
    def __init__(
            self,
            conn: asyncpg.Connection,
            *,
            adapter: Adapter | None = None,
    ) -> None:
        super().__init__()

        self._conn = conn
        if adapter is None:
            adapter = AsyncpgAdapter()
        self._adapter = adapter

    @property
    def adapter(self) -> Adapter:
        return self._adapter

    def query(self, query: Queryable) -> ta.AsyncContextManager[AsyncRows]:
        @contextlib.asynccontextmanager
        async def inner():
            q = check.isinstance(query, Query)

            tr = self._conn.transaction()
            await tr.start()
            try:
                stmt = await self._conn.prepare(q.text)
                columns = build_asyncpg_columns(stmt.get_attributes())
                cursor = await stmt.cursor(*q.args)

                yield AsyncpgRows(cursor, columns)

            except BaseException:
                await tr.rollback()
                raise

            else:
                await tr.commit()

        return inner()

    def begin(self) -> ta.AsyncContextManager[AsyncTxn]:
        return AsyncpgTxn(self)


#


class AsyncpgDb(AsyncDb):
    def __init__(
            self,
            connector: ta.Callable[[], ta.AsyncContextManager[asyncpg.Connection]],
            *,
            adapter: Adapter | None = None,
    ) -> None:
        super().__init__()

        self._connector = connector
        if adapter is None:
            adapter = AsyncpgAdapter()
        self._adapter = adapter

    @property
    def adapter(self) -> Adapter:
        return self._adapter

    async def _connect(
            self,
            es: contextlib.AsyncExitStack,
    ) -> AsyncpgConn:
        return AsyncpgConn(
            await es.enter_async_context(self._connector()),
            adapter=self._adapter,
        )

    def connect(self) -> ta.AsyncContextManager[AsyncConn]:
        @contextlib.asynccontextmanager
        async def inner():
            async with contextlib.AsyncExitStack() as es:
                yield await self._connect(es)

        return inner()

    def query(self, query: Queryable) -> ta.AsyncContextManager[AsyncRows]:
        @contextlib.asynccontextmanager
        async def inner():
            async with self.connect() as conn:
                async with conn.query(query) as rows:
                    yield rows

        return inner()


#


class AsyncpgAdapter(Adapter):
    @property
    def param_style(self) -> ParamStyle | None:
        return ParamStyle.DOLLAR_NUMERIC

    def scan_type(self, c: Column) -> type:
        raise NotImplementedError
