import contextlib

import pytest
import sqlalchemy as sa
import sqlalchemy.ext.asyncio

from ... import check
from ... import lang
from ...diag import pydevd as pdu  # noqa
from ...testing import pytest as ptu
from ..dbs import UrlDbLoc
from ..dbs import set_url_engine
from .dbs import Dbs


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
    schema='omlish',
)


##


def _test_mysql(url: str) -> None:
    with contextlib.ExitStack() as es:
        engine = sa.create_engine(url, echo=True)
        es.enter_context(lang.defer(engine.dispose))

        with engine.begin() as conn:
            conn.execute(sa.text('create database if not exists omlish'))
            conn.execute(sa.text('use omlish'))

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


@ptu.skip_if_cant_import('mysql.connector')
def test_mysql_mysql_connector_python(harness) -> None:
    url = check.isinstance(harness[Dbs].specs()['mysql'].loc, UrlDbLoc).url
    url = set_url_engine(url, 'mysql+mysqlconnector')
    _test_mysql(url)


@ptu.skip_if_cant_import('MySQLdb')
def test_mysql_mysqlclient(harness) -> None:
    url = check.isinstance(harness[Dbs].specs()['mysql'].loc, UrlDbLoc).url
    url = set_url_engine(url, 'mysql+mysqldb')
    _test_mysql(url)


@ptu.skip_if_cant_import('pymysql')
def test_mysql_pymysql(harness) -> None:
    url = check.isinstance(harness[Dbs].specs()['mysql'].loc, UrlDbLoc).url
    url = set_url_engine(url, 'mysql+pymysql')
    _test_mysql(url)


##


async def _test_mysql_async(url: str) -> None:
    async with contextlib.AsyncExitStack() as aes:
        engine = sa.ext.asyncio.create_async_engine(url, echo=True)
        await aes.enter_async_context(lang.a_defer(engine.dispose()))

        async with engine.begin() as conn:
            await conn.execute(sa.text('create database if not exists omlish'))
            await conn.execute(sa.text('use omlish'))

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


@ptu.skip_if_cant_import('aiomysql')
@pytest.mark.asyncio
async def test_async_mysql_aiomysql(harness) -> None:
    url = check.isinstance(harness[Dbs].specs()['mysql'].loc, UrlDbLoc).url
    url = set_url_engine(url, 'mysql+aiomysql')
    await _test_mysql_async(url)


@ptu.skip_if_cant_import('aiomysql')
@ptu.skip_if_cant_import('trio')
@ptu.skip_if_cant_import('trio_asyncio')
@pytest.mark.trio
async def test_trio_mysql_aiomysql(harness) -> None:
    url = check.isinstance(harness[Dbs].specs()['mysql'].loc, UrlDbLoc).url
    url = set_url_engine(url, 'mysql+aiomysql')

    import trio_asyncio  # noqa
    async with trio_asyncio.open_loop() as loop:  # noqa
        await trio_asyncio.aio_as_trio(_test_mysql_async)(url)
