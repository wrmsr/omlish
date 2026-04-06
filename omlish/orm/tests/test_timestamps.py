import concurrent.futures as cf
import contextlib
import datetime
import os.path
import sqlite3
import tempfile
import typing as ta

import pytest

from ... import dataclasses as dc
from ... import lang
from ... import orm
from ... import sql
from ...asyncs.asyncio import all as au


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class Kv:
    id: orm.Key[int] = dc.field(default_factory=orm.auto_key[int])

    key: str
    value: str

    created_at: datetime.datetime = orm.auto_value[datetime.datetime]()
    updated_at: datetime.datetime = orm.auto_value[datetime.datetime]()


@lang.cached_function
def registry() -> orm.Registry:
    return orm.registry(
        orm.dataclass_mapper(
            Kv,
            indexes=['key'],
            field_options=dict(
                created_at=[orm.CreatedAt()],
                updated_at=[orm.UpdatedAt()],
            ),
        ),
    )


async def _test_timestamps(store: orm.Store) -> None:
    async with orm.session(registry(), store):
        kv = await orm.add_one(Kv(key='hi', value='abcdef'))  # noqa
        await orm.flush()

    async with orm.session(registry(), store):
        kv2 = await orm.query_one(Kv, key='hi')  # noqa
        print(kv2)

    async with orm.session(registry(), store):
        kv = await orm.add_one(Kv(key='hi again', value='ghijkl'))  # noqa
        await orm.flush()
        await orm.refresh(kv)
        assert isinstance(kv.created_at, datetime.datetime)


@pytest.mark.asyncs('asyncio')
async def test_orm_in_memory():
    await _test_timestamps(orm.InMemoryStore())


@pytest.mark.asyncs('asyncio')
async def test_orm_sql():
    db_path = os.path.join(tempfile.mkdtemp(), 'orm.db')
    with cf.ThreadPoolExecutor(max_workers=1) as exe:
        db = sql.api.DbapiDb(lambda: contextlib.closing(sqlite3.connect(db_path)))
        adb = sql.api.SyncToAsyncDb(ta.cast(ta.Any, lambda: lang.ValueAsyncContextManager(au.ToThread(exe=exe))), db)
        store = orm.SqlStore(registry(), adb)
        await _test_timestamps(store)
