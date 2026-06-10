import pytest

from ...dtypes import Integer
from ...dtypes import String
from ..diffing import AddColumn
from ..diffing import AddIndex
from ..diffing import DropColumn
from ..diffing import DropIndex
from ..diffing import UnsupportedDiffError
from ..diffing import diff_table
from ..elements import Column
from ..elements import Elements
from ..elements import Index
from ..elements import PrimaryKey
from ..tabledefs import TableDef


def _td(*els):
    return TableDef('t', Elements(*els))


def test_add_and_drop_columns():
    existing = _td(Column('id', Integer()), PrimaryKey(['id']), Column('old', String()))
    current = _td(Column('id', Integer()), PrimaryKey(['id']), Column('new', String()))

    ops = diff_table(current, existing)

    assert {o.column.name for o in ops if isinstance(o, AddColumn)} == {'new'}
    assert {o.name for o in ops if isinstance(o, DropColumn)} == {'old'}


def test_add_and_drop_indexes():
    existing = _td(Column('id', Integer()), Index(['id'], name='old_ix'))
    current = _td(Column('id', Integer()), Index(['id'], name='new_ix'))

    assert {type(o) for o in diff_table(current, existing)} == {AddIndex, DropIndex}


def test_order_insensitive_no_change():
    a = _td(Column('a', Integer()), Column('b', Integer()), Index(['a'], name='x'))
    b = _td(Index(['a'], name='x'), Column('b', Integer()), Column('a', Integer()))

    assert diff_table(a, b) == []


def test_pk_change_raises():
    a = _td(Column('id', Integer()), Column('k', Integer()), PrimaryKey(['id']))
    b = _td(Column('id', Integer()), Column('k', Integer()), PrimaryKey(['k']))
    with pytest.raises(UnsupportedDiffError):
        diff_table(a, b)


def test_name_mismatch_raises():
    with pytest.raises(UnsupportedDiffError):
        diff_table(
            TableDef('a', Elements(Column('x', Integer()))),
            TableDef('b', Elements(Column('x', Integer()))),
        )
