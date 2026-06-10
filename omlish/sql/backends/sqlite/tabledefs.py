from .... import check
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
from ...tabledefs.rendering import StatementRenderer
from ...tabledefs.tabledefs import TableDef


##


CREATE_UPDATED_AT_TRIGGER_SRC = """\
create trigger {preamble} {trigger_name}
after update on {table_name}
for each row
when new.{column_name} = old.{column_name}
  begin
  update {table_name}
  set {column_name} = current_timestamp
  where {where};
end\
"""


class SqliteStatementRenderer(StatementRenderer):
    def column_type(self, c: Column, *, is_identity: bool) -> str:
        if isinstance(c.type, (String, Uuid)):
            return 'string'
        elif isinstance(c.type, Integer):
            return 'integer'
        elif isinstance(c.type, Datetime):
            return 'datetime'
        elif isinstance(c.type, Boolean):
            return 'boolean'
        elif isinstance(c.type, Float):
            return 'real'
        elif isinstance(c.type, Bytes):
            return 'blob'
        else:
            raise TypeError(c.type)

    def table_suffixes(self, tbl: TableDef, identity_column: str | None) -> list[str]:
        # A single integer-pk column is sqlite's implicit rowid; otherwise the table is WITHOUT ROWID.
        return [] if identity_column is not None else ['without rowid']

    def updated_at_trigger_statements(
            self,
            tbl: TableDef,
            e: UpdatedAtTrigger,
            pk: PrimaryKey | None,
            opts: StatementRenderer.CreateOptions,
    ) -> list[str]:
        if pk is not None:
            pk_cols = check.not_empty(pk.columns)
        else:
            pk_cols = ['rowid']

        return [CREATE_UPDATED_AT_TRIGGER_SRC.format(
            preamble='if not exists' if opts.if_not_exists else '',
            trigger_name=f'{tbl.name}__trigger__updated_at__{e.column}',
            table_name=tbl.name,
            column_name=e.column,
            where=' and '.join(f'{c} = new.{c}' for c in pk_cols),
        )]
