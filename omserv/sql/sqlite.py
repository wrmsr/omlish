import asyncio

import sqlalchemy as sa
import sqlalchemy.ext.asyncio


meta = sa.MetaData()
t1 = sa.Table(
    't1',
    meta,
    sa.Column('name', sa.String(50), primary_key=True),
)


async def _a_main() -> None:
    engine = sa.ext.asyncio.create_async_engine('sqlite+aiosqlite://', echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)

        await conn.execute(
            t1.insert(), [
                {'name': 'some name 1'},
                {'name': 'some name 2'},
            ]
        )

    async with engine.connect() as conn:
        # sa.select a Result, which will be delivered with buffered results
        result = await conn.execute(sa.select(t1).where(t1.c.name == 'some name 1'))

        print(result.fetchall())

    # for AsyncEngine created in function scope, close and clean-up pooled connections
    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(_a_main())
