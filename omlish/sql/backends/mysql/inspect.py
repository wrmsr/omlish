# ruff: noqa: S608
from ...api.querierfuncs import query_all
from ...api.queriers import AsyncQuerier
from ...dtypes import Datetime
from ...dtypes import Dtype
from ...dtypes import Integer
from ...dtypes import String
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


class MysqlInspector(Inspector):
    """
    Barebones information_schema reflection against the connection's current database. Fail-open: it models columns, the
    primary key, and explicitly-created (non-PRIMARY) indexes, ignoring the rest; table name interpolated as it is
    code-defined reflection, not user input.
    """

    async def reflect_table(self, querier: AsyncQuerier, name: str) -> ReflectedTable | None:
        rows = await query_all(querier, (
            'select column_name as name, data_type as type, is_nullable as nullable, column_key as ckey '
            'from information_schema.columns '
            f"where table_schema = database() and table_name = '{name}' "
            'order by ordinal_position'
        ))
        if not rows:
            return None

        cols: list[ReflectedColumn] = []
        for r in rows:
            d = r.to_dict()
            cols.append(ReflectedColumn(
                d['name'],
                d['type'],
                nullable=d['nullable'] == 'YES',
                primary_key=d['ckey'] == 'PRI',
            ))

        idx_cols: dict[str, list[str]] = {}
        idx_unique: dict[str, bool] = {}
        for r in await query_all(querier, (
            'select index_name as iname, column_name as cname, non_unique as nonuniq '
            'from information_schema.statistics '
            f"where table_schema = database() and table_name = '{name}' and index_name != 'PRIMARY' "
            'order by index_name, seq_in_index'
        )):
            d = r.to_dict()
            iname = d['iname']
            idx_cols.setdefault(iname, []).append(d['cname'])
            idx_unique[iname] = not bool(int(d['nonuniq']))

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
        elif tl in ('datetime', 'timestamp', 'date'):
            return Datetime()
        else:
            # fail-open: text/varchar/char/etc land as String for now.
            return String()
