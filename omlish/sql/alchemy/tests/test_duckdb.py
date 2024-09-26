import pytest
import sqlalchemy as sa

from .... import lang
from ....diag import pydevd as pdu
from ....testing import pytest as ptu
from .. import duckdb as _duckdb


##


@pytest.fixture(autouse=True)
def _patch_for_trio_asyncio_fixture():
    pdu.patch_for_trio_asyncio()


##


@ptu.skip.if_cant_import('duckdb')
def test_postgres_duckdb():
    url = _duckdb.DuckdbDialect.name + '://'

    with lang.disposing(sa.create_engine(url, echo=True)) as engine:
        with engine.connect() as conn:
            print(conn.execute(sa.text('select 1')).fetchall())
