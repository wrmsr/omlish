import sqlalchemy as sa

from ... import lang
from ...testing import pytest as ptu
from .. import sqlean as _sqlean
from .test_sqlite import _test_sqlite  # noqa


@ptu.skip_if_cant_import('sqlean')
def test_sqlite_sqlean():
    _test_sqlite(_sqlean.SqleanDialect.name)

    with lang.disposing(sa.create_engine(f'{_sqlean.SqleanDialect.name}://', echo=True)) as engine:
        with engine.connect() as conn:
            print(conn.execute(sa.text('select cos(0)')).fetchall())
