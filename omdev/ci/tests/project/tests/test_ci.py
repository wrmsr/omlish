import os
import subprocess


def test_imports():
    import anyio  # noqa
    import yaml  # noqa


# def test_async_pg():
#     import asyncio
#     import asyncpg
#
#     async def run():
#         conn = await asyncpg.connect(
#             host='omlish-postgres',
#             user='postgres',
#             password='omlish',
#         )
#
#         values = await conn.fetch(
#             'SELECT * FROM mytable WHERE id = $1',
#             10,
#         )
#
#         print(values)
#
#         await conn.close()
#
#     asyncio.run(run())


def test_pg_ping():
    if 'CI' not in os.environ:
        import pytest  # noqa
        pytest.skip('not in CI')

    subprocess.check_call([
        'ping',
        '-c', '1',
        'omlish-postgres',
    ])
