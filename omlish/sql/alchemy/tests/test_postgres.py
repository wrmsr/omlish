import contextlib

import pytest
import sqlalchemy as sa
import sqlalchemy.ext.asyncio

from .... import check
from .... import lang
from ....diag import pydevd as pdu
from ....testing import pytest as ptu
from ...dbs import UrlDbLoc
from ...dbs import set_url_engine
from ...tests.harness import HarnessDbs
from ...tests.utils import mark_sql_backend


##


@pytest.fixture(autouse=True)
def _patch_for_trio_asyncio_fixture():
    pdu.patch_for_trio_asyncio()


##


meta = sa.MetaData()
t1 = sa.Table(
    't1',
    meta,
    sa.Column('name', sa.String(50), primary_key=True),
)


##


def _test_postgres(url: str) -> None:
    with contextlib.ExitStack() as es:
        engine = sa.create_engine(url, echo=True)
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


@ptu.skip.if_cant_import('pg8000')
@mark_sql_backend('postgres')
def test_postgres_pg8000(harness) -> None:
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    url = set_url_engine(url, 'postgresql+pg8000')
    _test_postgres(url)


@ptu.skip.if_cant_import('psycopg2')
@mark_sql_backend('postgres')
def test_postgres_psycopg2(harness) -> None:
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    url = set_url_engine(url, 'postgresql+psycopg2')
    _test_postgres(url)


@ptu.skip.if_cant_import('psycopg')
@mark_sql_backend('postgres')
def test_postgres_psycopg(harness) -> None:
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    url = set_url_engine(url, 'postgresql+psycopg')
    _test_postgres(url)


##


async def _test_postgres_async(url: str) -> None:
    async with contextlib.AsyncExitStack() as aes:
        engine = sa.ext.asyncio.create_async_engine(url, echo=True)  # noqa
        await aes.enter_async_context(lang.adefer(engine.dispose()))

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


@ptu.skip.if_cant_import('asyncpg')
@pytest.mark.asyncs('asyncio')
@mark_sql_backend('postgres')
async def test_async_postgres_asyncpg(harness) -> None:
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    url = set_url_engine(url, 'postgresql+asyncpg')
    await _test_postgres_async(url)


@ptu.skip.if_cant_import('asyncpg')
@ptu.skip.if_cant_import('trio')
@ptu.skip.if_cant_import('trio_asyncio')
@pytest.mark.asyncs('trio')
@mark_sql_backend('postgres')
async def test_trio_postgres_asyncpg(harness) -> None:
    url = check.isinstance(check.isinstance(harness[HarnessDbs].specs()['postgres'].loc, UrlDbLoc).url, str)
    url = set_url_engine(url, 'postgresql+asyncpg')

    import trio_asyncio  # noqa
    async with trio_asyncio.open_loop() as loop:  # noqa
        await trio_asyncio.aio_as_trio(_test_postgres_async)(url)
