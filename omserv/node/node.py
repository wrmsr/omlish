import asyncio

import sqlalchemy as sa
import sqlalchemy.ext.asyncio

from ..secrets import load_secrets  # noqa


meta = sa.MetaData()

t1 = sa.Table(
    '_nodes',
    meta,
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('name', sa.String(50), nullable=False, unique=True),
)


async def _a_main() -> None:
    cfg = load_secrets()

    host = cfg['postgres_host']
    port = 5432
    user = cfg['postgres_user']
    password = cfg['postgres_pass']

    engine = sa.ext.asyncio.create_async_engine(f'postgresql+asyncpg://{user}:{password}@{host}:{port}', echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(meta.create_all)

        await conn.execute(
            t1.insert(), [
                {'name': 'home node'},
            ]
        )

    async with engine.connect() as conn:
        result = await conn.execute(
            sa.select(t1)
            # .where(t1.c.name == 'some name 1')
        )

        print(result.fetchall())

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(_a_main())
