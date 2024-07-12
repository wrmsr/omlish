import contextlib

import pytest
import sqlalchemy as sa
import sqlalchemy.ext.asyncio

from ... import check
from ... import lang
from ...testing import pytest as ptu
from ..dbs import UrlDbLoc
from ..dbs import set_url_engine
from .dbs import Dbs


meta = sa.MetaData()
t1 = sa.Table(
    't1',
    meta,
    sa.Column('name', sa.String(50), primary_key=True),
)


def test_postgres(harness) -> None:
    url = check.isinstance(harness[Dbs].specs()['postgres'].loc, UrlDbLoc).url
    url = set_url_engine(url, 'postgresql+pg8000')

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


@ptu.skip_if_cant_import('asyncpg')
@pytest.mark.asyncio
async def test_async_postgres(harness) -> None:
    url = check.isinstance(harness[Dbs].specs()['postgres'].loc, UrlDbLoc).url
    url = set_url_engine(url, 'postgresql+asyncpg')

    async with contextlib.AsyncExitStack() as aes:
        engine = sa.ext.asyncio.create_async_engine(url, echo=True)  # noqa
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
