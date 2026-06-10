from ...dtypes import Boolean
from ...dtypes import Bytes
from ...dtypes import Float
from ...tabledefs.elements import Column
from ..mysql.tabledefs import MysqlStatementRenderer
from ..postgres.tabledefs import PostgresStatementRenderer
from ..sqlite.tabledefs import SqliteStatementRenderer


def _types(r):
    return {t: r.column_type(Column('c', t), is_identity=False) for t in (Boolean(), Float(), Bytes())}


def test_new_dtypes_render_per_backend():
    assert _types(SqliteStatementRenderer()) == {Boolean(): 'boolean', Float(): 'real', Bytes(): 'blob'}
    assert _types(PostgresStatementRenderer()) == {Boolean(): 'boolean', Float(): 'double precision', Bytes(): 'bytea'}
    assert _types(MysqlStatementRenderer()) == {Boolean(): 'tinyint(1)', Float(): 'double', Bytes(): 'blob'}
