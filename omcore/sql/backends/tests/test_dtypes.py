from ...dtypes import Boolean
from ...dtypes import Bytes
from ...dtypes import Float
from ...tabledefs.elements import Column
from ..mysql.tabledefs import MysqlTabledefRenderer
from ..postgres.tabledefs import PostgresTabledefRenderer
from ..sqlite.tabledefs import SqliteTabledefRenderer


def _types(r):
    return {t: r.column_type(Column('c', t), is_identity=False) for t in (Boolean(), Float(), Bytes())}


def test_new_dtypes_render_per_backend():
    assert _types(SqliteTabledefRenderer()) == {Boolean(): 'boolean', Float(): 'real', Bytes(): 'blob'}
    assert _types(PostgresTabledefRenderer()) == {Boolean(): 'boolean', Float(): 'double precision', Bytes(): 'bytea'}
    assert _types(MysqlTabledefRenderer()) == {Boolean(): 'tinyint(1)', Float(): 'double', Bytes(): 'blob'}
