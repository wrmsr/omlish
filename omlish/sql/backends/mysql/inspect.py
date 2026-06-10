# ruff: noqa: S608
from ...api.querierfuncs import query_all
from ...api.queriers import Querier
from ...dtypes import Datetime
from ...dtypes import Dtype
from ...dtypes import Integer
from ...dtypes import String
from ...inspect.inspectors import Inspector
from ...inspect.reflected import ReflectedColumn
from ...inspect.reflected import ReflectedTable
from ...tabledefs.elements import Column
from ...tabledefs.elements import Element
from ...tabledefs.elements import Elements
from ...tabledefs.elements import PrimaryKey
from ...tabledefs.tabledefs import TableDef


##


class MysqlInspector(Inspector):
    """
    Barebones information_schema reflection against the connection's current database. Fail-open (it models columns +
    primary key, ignoring the rest); table name interpolated as it is code-defined reflection, not user input.
    """

    def reflect_table(self, querier: Querier, name: str) -> ReflectedTable | None:
        rows = query_all(querier, (
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
        elif tl in ('datetime', 'timestamp', 'date'):
            return Datetime()
        else:
            # fail-open: text/varchar/char/etc land as String for now.
            return String()
