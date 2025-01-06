"""
TODO:
 - https://github.com/asg017/sqlite-vec/tree/main
"""
import contextlib

import pytest
import sqlalchemy as sa
import sqlalchemy.ext.asyncio

from .... import lang
from ....testing import pytest as ptu


##


meta = sa.MetaData()
t1 = sa.Table(
    't1',
    meta,
    sa.Column('name', sa.String(50), primary_key=True),
)


##


def _test_sqlite(scheme: str) -> None:
    with contextlib.ExitStack() as es:
        engine = sa.create_engine(f'{scheme}://', echo=True)
        es.enter_context(lang.defer(engine.dispose))

        with engine.begin() as conn:
            meta.drop_all(bind=conn)
            meta.create_all(bind=conn)

            conn.execute(
                t1.insert(), [
                    {'name': 'some name 1'},
                    {'name': 'some name 2'},
                ],
            )

        with engine.connect() as conn:
            result = conn.execute(sa.select(t1).where(t1.c.name == 'some name 1'))
            rows = list(result.fetchall())
            assert len(rows) == 1
            assert rows[0].name == 'some name 1'

            print(conn.execute(sa.text('select sqlite_version()')).fetchall())


def test_sqlite():
    _test_sqlite('sqlite')


##


async def _test_async_sqlite(scheme: str) -> None:
    async with contextlib.AsyncExitStack() as aes:
        engine = sa.ext.asyncio.create_async_engine(f'{scheme}://', echo=True)
        await aes.enter_async_context(lang.a_defer(engine.dispose()))

        async with engine.begin() as conn:
            await conn.run_sync(meta.drop_all)
            await conn.run_sync(meta.create_all)

            await conn.execute(
                t1.insert(), [
                    {'name': 'some name 1'},
                    {'name': 'some name 2'},
                ],
            )

        async with engine.connect() as conn:
            result = await conn.execute(sa.select(t1).where(t1.c.name == 'some name 1'))
            rows = list(result.fetchall())
            assert len(rows) == 1
            assert rows[0].name == 'some name 1'


@ptu.skip.if_cant_import('aiosqlite')
@ptu.skip.if_cant_import('greenlet')
@pytest.mark.asyncs('asyncio')
async def test_async_sqlite():
    await _test_async_sqlite('sqlite+aiosqlite')
