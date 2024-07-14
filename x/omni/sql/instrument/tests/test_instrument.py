import pytest
import sqlalchemy as sa
import sqlalchemy.pool  # noqa

from .... import lang
from ....docker.dev.pytest import DockerManager
from ....inject.dev import pytest as ptinj


def test_instrument_sqlite():
    for c in [
        'o_sqlite://',
        'o_sqlite+pysqlite://',
    ]:
        for _ in range(2):
            engine: sa.engine.Engine
            with lang.disposing(
                    sa.create_engine(
                        c,
                        connect_args={'check_same_thread': False},
                        poolclass=sa.pool.StaticPool,
                    )
            ) as engine:
                with engine.connect() as conn:
                    print(list(conn.execute('select 1')))


def test_instrument_mysql(harness: ptinj.Harness):
    [(host, port)] = harness[DockerManager].get_container_tcp_endpoints([('mysql-master', 3306)]).values()
    for c in [
        f'o_mysql+mysqlconnector://omnibus:omnibus@{host}:{port}',
        f'o_mysql+pymysql://omnibus:omnibus@{host}:{port}',
        # f'o_mysql://omnibus:omnibus@{host}:{port}',
    ]:
        for _ in range(2):
            engine: sa.engine.Engine
            with lang.disposing(sa.create_engine(c)) as engine:
                with engine.connect() as conn:
                    print(list(conn.execute('select 1')))


@pytest.mark.no_ci
def test_instrument_postgres(harness: ptinj.Harness):
    [(host, port)] = harness[DockerManager].get_container_tcp_endpoints([('postgres-master', 5432)]).values()
    for c in [
        f'o_postgresql+psycopg2://omnibus:omnibus@{host}:{port}',
        f'o_postgresql+pg8000://omnibus:omnibus@{host}:{port}',
        f'o_postgresql://omnibus:omnibus@{host}:{port}',
    ]:
        for _ in range(2):
            engine: sa.engine.Engine
            with lang.disposing(sa.create_engine(c)) as engine:
                with engine.connect() as conn:
                    print(list(conn.execute('select 1')))
