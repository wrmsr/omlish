"""
plan:
 - create table without rowid
 - primary key clustered (`chat_id`, `seq`)
 - unique not null non-pk index on `id`
"""
import concurrent.futures as cf
import contextlib
import datetime
import os.path
import sqlite3
import tempfile
import typing as ta
import uuid

import pytest

from ... import dataclasses as dc
from ... import lang
from ... import orm
from ... import sql
from ...asyncs.asyncio import all as au
from ..registries import Registry
from ..sql import SqlStore
from ..stores import Store


##


@dc.dataclass(kw_only=True)
class _Base(lang.Abstract):
    created_at: datetime.datetime = orm.auto_value[datetime.datetime]()
    updated_at: datetime.datetime = orm.auto_value[datetime.datetime]()


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class DriverChat(_Base):
    id: orm.Key[uuid.UUID] = dc.field(default_factory=orm.key_wrapping(uuid.uuid4))

    num_messages: int = 0

    messages: ta.ClassVar[orm.Backref['DriverMessage']] = orm.backref(lambda: DriverMessage.chat)  # type: ignore[misc]


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class DriverMessage(_Base):
    id: orm.Key[uuid.UUID] = dc.field(default_factory=orm.key_wrapping(uuid.uuid4))

    chat: orm.Ref[DriverChat, uuid.UUID]
    seq: int

    text: str


##


def build_registry() -> orm.Registry:
    base_field_options: dict[str, ta.Sequence[orm.FieldOption]] = dict(
        created_at=[orm.CreatedAt()],
        updated_at=[orm.UpdatedAt()],
    )

    return orm.registry(

        orm.dataclass_mapper(
            DriverChat,
            field_options=dict(
                **base_field_options,
            ),
        ),

        orm.dataclass_mapper(
            DriverMessage,
            field_options=dict(
                **base_field_options,
            ),
        ),

    )


##


async def _test_orm(store: Store, registry: Registry | None = None) -> None:
    if registry is None:
        registry = build_registry()  # noqa

    pass  # noqa


@pytest.mark.asyncs('asyncio')
async def test_orm_in_memory():
    await _test_orm(orm.InMemoryStore())


@pytest.mark.asyncs('asyncio')
async def test_orm_sql():
    db_path = os.path.join(tempfile.mkdtemp(), 'orm.db')
    registry = build_registry()
    with cf.ThreadPoolExecutor(max_workers=1) as exe:
        db = sql.api.DbapiDb(lambda: contextlib.closing(sqlite3.connect(db_path)))
        adb = sql.api.SyncToAsyncDb(ta.cast(ta.Any, lambda: lang.ValueAsyncContextManager(au.ToThread(exe=exe))), db)
        store = SqlStore(registry, adb)
        await _test_orm(store, registry)
