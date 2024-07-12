import contextlib

import pytest
import sqlalchemy as sa
import sqlalchemy.ext.asyncio

from ... import lang
from ...testing import pytest as ptu


meta = sa.MetaData()
t1 = sa.Table(
    't1',
    meta,
    sa.Column('name', sa.String(50), primary_key=True),
)


@ptu.skip_if_cant_import('asyncpg')
@pytest.mark.asyncio
async def test_async_postgres() -> None:
    port = 35225

    async with contextlib.AsyncExitStack() as aes:
        engine = sa.ext.asyncio.create_async_engine(f'postgresql+asyncpg://omlish:omlish@localhost:{port}', echo=True)  # noqa
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
