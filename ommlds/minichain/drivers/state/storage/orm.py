import concurrent.futures as cf
import contextlib
import datetime
import sqlite3
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
from omlish import orm
from omlish import sql
from omlish.asyncs.asyncio import all as au
from omlish.formats import json

from .marshaled import MarshaledStateStorage


T = ta.TypeVar('T')


##


@dc.dataclass(kw_only=True)
@dc.extra_class_params(install_class_field_attrs='instance')
class State:
    id: orm.Key[int] = dc.field(default_factory=orm.auto_key)

    key: str
    value: str

    created_at: datetime.datetime = orm.auto_value[datetime.datetime]()
    updated_at: datetime.datetime = orm.auto_value[datetime.datetime]()


@lang.cached_function
def registry() -> orm.Registry:
    return orm.registry(
        orm.dataclass_mapper(
            State,
            indexes=['key'],
            field_options=dict(
                created_at=[orm.CreatedAt()],
                updated_at=[orm.UpdatedAt()],
            ),
        ),
    )


##


class OrmStateStorage(MarshaledStateStorage):
    @dc.dataclass(frozen=True, kw_only=True)
    class Config:
        file: str = dc.xfield(coerce=check.non_empty_str)

    def __init__(self, config: Config) -> None:
        super().__init__()

        self._config = config

    def _session(self) -> ta.AsyncContextManager[orm.Session]:
        @contextlib.asynccontextmanager
        async def inner():
            with cf.ThreadPoolExecutor(max_workers=1) as exe:
                db = sql.api.DbapiDb(lambda: contextlib.closing(sqlite3.connect(
                    self._config.file,
                )))

                adb = sql.api.SyncToAsyncDb(
                    ta.cast(ta.Any, lambda: lang.ValueAsyncContextManager(au.ToThread(exe=exe))),
                    db,
                )

                reg = registry()

                store = orm.SqlStore(reg, adb)

                async with orm.session(reg, store) as sess:
                    yield sess

        return inner()

    async def load_state(self, key: str, ty: type[T] | None) -> T | None:
        async with self._session():
            rows = await orm.query(State, key=key)
            if not rows:
                return None

            row = check.single(rows)

            mj = row.value
            mv = json.loads(mj)
            obj = self._unmarshal_state(mv, ty)
            return obj

    async def save_state(self, key: str, obj: ta.Any | None, ty: type[T] | None) -> None:
        mj: str | None = None
        if obj is not None:
            mv = self._marshal_state(obj, ty)
            mj = json.dumps(mv)

        async with self._session():
            rows = await orm.query(State, key=key)

            if not rows:
                if mj is not None:
                    await orm.add(State(key=key, value=mj))

            else:
                row = check.single(rows)

                if mj is not None:
                    row.value = mj

                else:
                    await orm.delete(row)
