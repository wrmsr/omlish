import asyncio

import sqlalchemy as sa
import sqlalchemy.ext.asyncio

from omlish import check

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

    node_name = 'home node'

    async with engine.connect() as conn:
        async with conn.begin() as txn:
            await conn.run_sync(meta.drop_all)

            await conn.run_sync(meta.create_all)

            await conn.begin()

            result = await conn.execute(sa.select(t1).where(t1.c.name == node_name))
            result_rows = result.fetchall()

            if len(result_rows) > 0:
                node_row = check.single(result_rows)
                node_id = node_row['id']
            else:
                result = await conn.execute(t1.insert(), [{'name': 'home node'}])
                node_id = check.single(result.inserted_primary_key)

            result = await conn.execute(sa.select(sa.func.pg_advisory_lock(sa.column('id'))).select_from(t1))
            print(result.fetchall())

            result = await conn.execute(sa.select(t1))
            print(result.fetchall())

    await engine.dispose()


if __name__ == '__main__':
    asyncio.run(_a_main())
