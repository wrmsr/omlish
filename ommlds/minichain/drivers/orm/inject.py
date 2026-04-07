import contextlib
import os.path
import typing as ta

from omlish import check
from omlish import inject as inj
from omlish import orm

from .configs import OrmConfig
from .impl import OrmImpl
from .types import Orm


##


def _provide_registry(mappers: ta.AbstractSet[orm.Mapper]) -> orm.Registry:
    return orm.registry(*mappers)


#


_SqlStoreFilePath = ta.NewType('_SqlStoreFilePath', str)


async def _provide_sql_store(
        file_path: _SqlStoreFilePath,
        registry: orm.Registry,
) -> orm.SqlStore:
    import concurrent.futures as cf
    import sqlite3

    from omlish import sql
    from omlish.asyncs.asyncio import all as au

    @contextlib.asynccontextmanager
    async def executor():
        with cf.ThreadPoolExecutor(max_workers=1) as exe:
            yield au.ToThread(exe=exe)

    def connect():
        if not file_path.startswith(':'):
            db_dir = os.path.dirname(file_path)
            os.makedirs(db_dir, exist_ok=True)
            # os.chmod(state_dir, 0o770)  # noqa

        return sqlite3.connect(
            file_path,
        )

    db = sql.api.DbapiDb(lambda: contextlib.closing(connect()))

    adb = sql.api.SyncToAsyncDb(
        executor,
        db,
    )

    return orm.SqlStore(registry, adb)


#


def bind_orm(cfg: OrmConfig = OrmConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.set_binder[orm.Mapper](),
        inj.bind(_provide_registry, singleton=True),
    ])

    #

    if cfg.file_path is not None:
        db_fp = check.non_empty_str(cfg.file_path)

        if db_fp.endswith('.db'):
            els.extend([
                inj.bind(_SqlStoreFilePath, to_const=db_fp),
                inj.bind(_provide_sql_store, singleton=True),
                inj.bind(orm.Store, to_key=orm.SqlStore),
            ])

        else:
            raise NotImplementedError(db_fp)

    else:
        els.extend([
            inj.bind(orm.InMemoryStore()),
            inj.bind(orm.Store, to_key=orm.InMemoryStore),
        ])

    #

    els.extend([
        inj.bind(OrmImpl, singleton=True),
        inj.bind(Orm, to_key=OrmImpl),
    ])

    #

    return inj.as_elements(*els)
