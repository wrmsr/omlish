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


class SqliteInspector(Inspector):
    async def reflect_table(self, querier: AsyncQuerier, name: str) -> ReflectedTable | None:
        info = await query_all(querier, f'pragma table_info({name})')
        if not info:
            return None

        cols: list[ReflectedColumn] = []
        for row in info:
            d = row.to_dict()
            cols.append(ReflectedColumn(
                d['name'],
                d['type'],
                nullable=not d['notnull'],
                primary_key=bool(d['pk']),
            ))

        idxs: list[ReflectedIndex] = []
        for irow in await query_all(querier, f'pragma index_list({name})'):
            idd = irow.to_dict()
            if idd.get('origin') != 'c':
                continue  # only explicit CREATE INDEXes are modeled; skip pk- and unique-constraint-backed indexes
            iname = idd['name']
            icols = [r.to_dict()['name'] for r in await query_all(querier, f'pragma index_info({iname})')]
            idxs.append(ReflectedIndex(iname, icols, unique=bool(idd['unique'])))

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
        elif tl in ('datetime', 'timestamp'):
            return Datetime()
        else:
            # fail-open: text/string/varchar/blob/anything-else lands as String for now.
            return String()
