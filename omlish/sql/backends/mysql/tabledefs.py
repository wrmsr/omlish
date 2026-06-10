from ...dtypes import Boolean
from ...dtypes import Bytes
from ...dtypes import Datetime
from ...dtypes import Float
from ...dtypes import Integer
from ...dtypes import String
from ...dtypes import Uuid
from ...tabledefs.elements import Column
from ...tabledefs.elements import PrimaryKey
from ...tabledefs.elements import UpdatedAtTrigger
from ...tabledefs.rendering import RenderColumn
from ...tabledefs.rendering import StatementRenderer
from ...tabledefs.tabledefs import TableDef


##


CREATE_UPDATED_AT_TRIGGER_SRC = """\
create trigger {trigger_name}
before update on {table_name}
for each row
set new.{column_name} = current_timestamp\
"""


class MysqlStatementRenderer(StatementRenderer):
    def column_type(self, c: Column, *, is_identity: bool) -> str:
        if isinstance(c.type, String):
            return 'text'
        elif isinstance(c.type, Uuid):
            return 'char(36)'
        elif isinstance(c.type, Integer):
            return 'bigint' if is_identity else 'integer'
        elif isinstance(c.type, Datetime):
            return 'datetime'
        elif isinstance(c.type, Boolean):
            return 'tinyint(1)'
        elif isinstance(c.type, Float):
            return 'double'
        elif isinstance(c.type, Bytes):
            return 'blob'
        else:
            raise TypeError(c.type)

    def column_identity_sql(self, c: Column) -> str:
        return 'auto_increment'

    def _render_column(self, rc: RenderColumn) -> str:
        # MySQL wants AUTO_INCREMENT *after* NOT NULL / DEFAULT, unlike postgres' identity clause - so the column-clause
        # ordering is genuinely dialect-specific. (A cleaner base would expose the ordering as a hook; for now mysql
        # overrides the whole thing.)
        parts = [f'{rc.name} {rc.type}']
        if rc.not_null:
            parts.append('not null')
        if rc.default is not None:
            parts.append(f'default {rc.default}')
        if rc.identity:
            parts.append(rc.identity)
        parts.extend(rc.extra)
        return ' '.join(parts)

    def updated_at_trigger_statements(
            self,
            tbl: TableDef,
            e: UpdatedAtTrigger,
            pk: PrimaryKey | None,
            opts: StatementRenderer.CreateOptions,
    ) -> list[str]:
        return [CREATE_UPDATED_AT_TRIGGER_SRC.format(
            trigger_name=f'{tbl.name}__trigger__updated_at__{e.column}',
            table_name=tbl.name,
            column_name=e.column,
        )]
