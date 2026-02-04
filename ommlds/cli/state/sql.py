import asyncio
import contextlib
import sqlite3
import typing as ta

from omlish import dataclasses as dc
from omlish import sql
from omlish.sql import Q

from .storage import MarshalStateStorage


T = ta.TypeVar('T')


##


STATES = sql.td.table_def(
    'states',

    sql.td.Column('key', sql.td.String()),
    sql.td.Column('value', sql.td.String()),

    sql.td.CreatedAtUpdatedAt(),
)


class SqlStateStorage(MarshalStateStorage):
    @dc.dataclass(frozen=True, kw_only=True)
    class Config:
        file: str | None = None

    def __init__(self, config: Config = Config()) -> None:
        super().__init__()

        self._config = config

        self._has_created = False

    def _create_table_if_necessary(self, db: sql.api.Querier) -> None:
        if not self._has_created:
            for stmt in sql.td.render_create_statements(sql.td.lower_table_elements(STATES)):
                sql.api.exec(db, stmt)

            self._has_created = True

    async def _run_with_db(self, fn: ta.Callable[[sql.api.Conn], T]) -> T:
        def inner():
            db = sql.api.DbapiDb(lambda: contextlib.closing(sqlite3.connect(
                self._config.file or ':memory:',
            )))

            with db.connect() as conn:
                return fn(conn)

        return await asyncio.to_thread(inner)

    async def load_state(self, key: str, ty: type[T] | None) -> T | None:
        def inner(db: sql.api.Conn) -> sql.api.Row | None:
            self._create_table_if_necessary(db)

            return sql.api.query_opt_one(db, Q.select([Q.i.value], Q.n.states, Q.eq(Q.n.key, key)))

        row = await self._run_with_db(inner)
        if row is None:
            return None

        raise NotImplementedError

    async def save_state(self, key: str, obj: ta.Any | None, ty: type[T] | None) -> None:
        def inner(db: sql.api.Conn) -> sql.api.Row | None:
            self._create_table_if_necessary(db)

            with db.begin() as txn:
                # if sql.api.query_scalar(txn, Q.exists(Q.n.states, Q.eq(Q.n.key, key))) is not None:
                #     raise NotImplementedError

                sql.api.exec(txn, Q.insert([Q.i.key, Q.i.value], Q.n.states, [key, obj]))

            raise NotImplementedError

        await self._run_with_db(inner)
