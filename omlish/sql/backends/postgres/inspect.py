# ruff: noqa: S608
from ...api.querierfuncs import query_all
from ...api.queriers import AsyncQuerier
from ...dtypes import Datetime
from ...dtypes import Dtype
from ...dtypes import Integer
from ...dtypes import String
from ...dtypes import Uuid
from ...inspect.inspectors import Inspector
from ...inspect.reflected import ReflectedColumn
from ...inspect.reflected import ReflectedTable
from ...tabledefs.elements import Column
from ...tabledefs.elements import Element
from ...tabledefs.elements import Elements
from ...tabledefs.elements import PrimaryKey
from ...tabledefs.tabledefs import TableDef


##


class PostgresInspector(Inspector):
    """
    Barebones information_schema reflection. Fail-open: it models columns and the primary key; index reflection (and
    everything more exotic) is left for later, deliberately ignored rather than fatal. The table name is interpolated
    (not parameterized) because the param placeholder is driver-specific - acceptable here as it comes from code, not
    user input, and is reflection-only.
    """

    async def reflect_table(self, querier: AsyncQuerier, name: str) -> ReflectedTable | None:
        cols_rows = await query_all(querier, (
            "select column_name, data_type, is_nullable "
            "from information_schema.columns "
            f"where table_schema = 'public' and table_name = '{name}' "
            "order by ordinal_position"
        ))
        if not cols_rows:
            return None

        pk_cols = {
            r.to_dict()['column_name']
            for r in await query_all(querier, (
                "select kcu.column_name "
                "from information_schema.table_constraints tc "
                "join information_schema.key_column_usage kcu on kcu.constraint_name = tc.constraint_name "
                f"where tc.table_schema = 'public' and tc.table_name = '{name}' "
                "and tc.constraint_type = 'PRIMARY KEY'"
            ))
        }

        cols: list[ReflectedColumn] = []
        for r in cols_rows:
            d = r.to_dict()
            cols.append(ReflectedColumn(
                d['column_name'],
                d['data_type'],
                nullable=d['is_nullable'] == 'YES',
                primary_key=d['column_name'] in pk_cols,
            ))

        return ReflectedTable(name, cols)

    def lift_table(self, reflected: ReflectedTable) -> TableDef:
        els: list[Element] = []
        pk: list[str] = []
        for rc in reflected.columns:
            els.append(Column(rc.name, self._lift_dtype(rc.type), nullable=rc.nullable))
            if rc.primary_key:
                pk.append(rc.name)
        if pk:
            els.append(PrimaryKey(pk))
        return TableDef(reflected.name, Elements(*els))

    def _lift_dtype(self, t: str) -> Dtype:
        tl = t.strip().lower()
        if 'int' in tl:
            return Integer()
        elif 'timestamp' in tl or tl == 'date':
            return Datetime()
        elif tl == 'uuid':
            return Uuid()
        else:
            # fail-open: text/varchar/char/etc land as String for now.
            return String()
