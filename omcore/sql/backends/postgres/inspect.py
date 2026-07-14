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
from ...inspect.reflected import ReflectedIndex
from ...inspect.reflected import ReflectedTable
from ...tabledefs.elements import Column
from ...tabledefs.elements import Element
from ...tabledefs.elements import Elements
from ...tabledefs.elements import Index
from ...tabledefs.elements import PrimaryKey
from ...tabledefs.tabledefs import TableDef


##


class PostgresInspector(Inspector):
    """
    Barebones reflection. Fail-open: it models columns, the primary key, and explicitly-created (non-primary) indexes;
    anything more exotic is deliberately ignored rather than fatal. The table name is interpolated (not parameterized)
    because the param placeholder is driver-specific - acceptable here as it comes from code, not user input, and is
    reflection-only.
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

        idx_cols: dict[str, list[str]] = {}
        idx_unique: dict[str, bool] = {}
        for r in await query_all(querier, (
            'select i.relname as index_name, ix.indisunique as is_unique, a.attname as column_name '
            'from pg_class t '
            'join pg_index ix on ix.indrelid = t.oid '
            'join pg_class i on i.oid = ix.indexrelid '
            'join lateral unnest(ix.indkey) with ordinality as k(attnum, ord) on true '
            'join pg_attribute a on a.attrelid = t.oid and a.attnum = k.attnum '
            f"where t.relname = '{name}' and t.relkind = 'r' and not ix.indisprimary "
            'order by i.relname, k.ord'
        )):
            d = r.to_dict()
            iname = d['index_name']
            idx_cols.setdefault(iname, []).append(d['column_name'])
            idx_unique[iname] = bool(d['is_unique'])

        idxs = [ReflectedIndex(nm, cs, unique=idx_unique[nm]) for nm, cs in idx_cols.items()]

        return ReflectedTable(name, cols, indexes=idxs)

    def lift_table(self, reflected: ReflectedTable) -> TableDef:
        els: list[Element] = []
        pk: list[str] = []
        for rc in reflected.columns:
            els.append(Column(rc.name, self._lift_dtype(rc.type), nullable=rc.nullable))
            if rc.primary_key:
                pk.append(rc.name)
        if pk:
            els.append(PrimaryKey(pk))
        for ri in reflected.indexes:
            els.append(Index(ri.columns, name=ri.name, unique=ri.unique))
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
