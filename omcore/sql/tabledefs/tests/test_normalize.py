from ...dtypes import Integer
from ...dtypes import String
from ..elements import Column
from ..elements import Elements
from ..elements import Index
from ..elements import PrimaryKey
from ..lower import normalize_table
from ..tabledefs import TableDef


def test_normalize_is_order_insensitive_for_non_columns():
    a = TableDef('t', Elements(
        Column('id', Integer()),
        PrimaryKey(['id']),
        Column('name', String()),
        Index(['name'], name='by_name'),
        Index(['id'], name='by_id'),
    ))
    b = TableDef('t', Elements(
        Index(['id'], name='by_id'),
        Column('id', Integer()),
        Index(['name'], name='by_name'),
        Column('name', String()),
        PrimaryKey(['id']),
    ))

    assert normalize_table(a) == normalize_table(b)


def test_normalize_preserves_column_order():
    td = TableDef('t', Elements(
        Column('b', Integer()),
        Column('a', Integer()),
        Index(['a']),
    ))

    assert [c.name for c in normalize_table(td).elements[Column]] == ['b', 'a']
