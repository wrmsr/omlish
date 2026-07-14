import contextlib
import os.path
import typing as ta

from omcore import check
from omcore import inject as inj
from omcore import orm

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
            yield au.ToExecutor(exe)

    def connect():
        if not file_path.startswith(':'):
            db_dir = os.path.dirname(file_path)
            os.makedirs(db_dir, exist_ok=True)
            # os.chmod(state_dir, 0o770)  # noqa

        conn = sqlite3.connect(
            file_path,
        )

        try:
            mode = conn.execute('pragma journal_mode=wal').fetchone()[0]
            if str(mode).lower() != 'wal':
                raise RuntimeError(f'failed to enable WAL mode: {mode!r}')

            return conn

        except BaseException:
            conn.close()
            raise

    db = sql.api.DbapiDb(
        lambda: contextlib.closing(connect()),
        adapter=sql.be.sqlite.adapters.sqlite_adapter(),
    )

    adb = sql.api.SyncToAsyncDb(
        executor,
        db,
    )

    return orm.SqlStore(registry, adb, tabledef_renderer=sql.be.sqlite.td.SqliteTabledefRenderer())


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
