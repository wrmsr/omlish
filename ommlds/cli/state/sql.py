import asyncio
import contextlib
import sqlite3
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import sql
from omlish.formats import json
from omlish.sql import Q

from .marshaled import MarshaledStateStorage


T = ta.TypeVar('T')


##


STATES = sql.td.table_def(
    'states',

    sql.td.Column('key', sql.td.String()),
    sql.td.Column('value', sql.td.String()),

    sql.td.CreatedAtUpdatedAt(),
)


class SqlStateStorage(MarshaledStateStorage):
    @dc.dataclass(frozen=True, kw_only=True)
    class Config:
        file: str = dc.xfield(coerce=check.non_empty_str)

    def __init__(self, config: Config) -> None:
        super().__init__()

        self._config = config

        self._has_created = False

    def _create_table_if_necessary(self, db: sql.api.Querier) -> None:
        if not self._has_created:
            for stmt in sql.td.render_create_statements(
                    sql.td.lower_table_elements(STATES),
                    if_not_exists=True,
            ):
                sql.api.exec(db, stmt)

            self._has_created = True

    async def _run_with_db(self, fn: ta.Callable[[sql.api.Conn], T]) -> T:
        def inner():
            db = sql.api.DbapiDb(
                lambda: contextlib.closing(sqlite3.connect(
                    self._config.file,
                    autocommit=True,
                )),
                param_style=sql.ParamStyle.QMARK,
            )

            with db.connect() as conn:
                return fn(conn)

        return await asyncio.to_thread(inner)

    async def load_state(self, key: str, ty: type[T] | None) -> T | None:
        def inner(db: sql.api.Conn) -> sql.api.Row | None:
            self._create_table_if_necessary(db)

            return sql.api.query_opt_one(db, Q.select(
                [Q.i.value],
                Q.n.states,
                Q.eq(Q.n.key, key),
            ))

        row = await self._run_with_db(inner)
        if row is None:
            return None

        mj = row.c.value
        mv = json.loads(mj)
        obj = self._unmarshal_state(mv, ty)
        return obj

    async def save_state(self, key: str, obj: ta.Any | None, ty: type[T] | None) -> None:
        mj: str | None = None
        if obj is not None:
            mv = self._marshal_state(obj, ty)
            mj = json.dumps(mv)

        def inner(db: sql.api.Conn) -> None:
            self._create_table_if_necessary(db)

            with db.begin() as txn:
                if mj is None:
                    sql.api.exec(txn, Q.delete(
                        Q.n.states,
                        where=Q.eq(Q.n.key, key),
                    ))

                elif sql.api.query_scalar(txn, Q.select([Q.f.exists(Q.select(
                    [1],
                    Q.n.states,
                    Q.eq(Q.n.key, key),
                ))])):
                    sql.api.exec(txn, Q.update(
                        Q.n.states,
                        [(Q.i.value, mj)],
                        where=Q.eq(Q.i.key, key),
                    ))

                else:
                    sql.api.exec(txn, Q.insert(
                        [Q.i.key, Q.i.value],
                        Q.n.states,
                        [key, mj],
                    ))

        await self._run_with_db(inner)
