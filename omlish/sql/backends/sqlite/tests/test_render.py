from ....dtypes import String
from ....tabledefs.elements import Column
from ....tabledefs.elements import CreatedAtUpdatedAt
from ....tabledefs.elements import Elements
from ....tabledefs.elements import IdIntegerPrimaryKey
from ....tabledefs.elements import Index
from ....tabledefs.lower import lower_table_elements
from ....tabledefs.tabledefs import TableDef
from ..tabledefs import SqliteStatementRenderer


def test_render_golden():
    tbl = lower_table_elements(TableDef('users', Elements(
        IdIntegerPrimaryKey(),
        CreatedAtUpdatedAt(),
        Column('name', String()),
        Index(['name']),
    )))

    assert SqliteStatementRenderer().render_create_statements(tbl) == [
        (
            'create table users (\n'
            '  id integer not null,\n'
            '  created_at datetime not null default current_timestamp,\n'
            '  updated_at datetime not null default current_timestamp,\n'
            '  name string not null,\n'
            '  primary key (id)\n'
            ')'
        ),
        'create index users__index__name on users (name)\n',
        (
            'create trigger  users__trigger__updated_at__updated_at\n'
            'after update on users\n'
            'for each row\n'
            'when new.updated_at = old.updated_at\n'
            '  begin\n'
            '  update users\n'
            '  set updated_at = current_timestamp\n'
            '  where id = new.id;\n'
            'end'
        ),
    ]
