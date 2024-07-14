import typing as ta

import sqlalchemy as sa
import sqlalchemy.engine.reflection

from .. import check
from .. import collections as col
from .. import properties


class Inspection:

    def __init__(self, inspector: sa.engine.reflection.Inspector) -> None:
        super().__init__()
        self._inspector = check.isinstance(inspector, sa.engine.reflection.Inspector)

    @properties.cached
    def schema_names(self) -> ta.FrozenSet[str]:
        return frozenset(self._inspector.get_schema_names())

    @properties.cached
    def table_names(self) -> ta.FrozenSet[str]:
        return frozenset(self._inspector.get_table_names())

    @properties.cached
    def table_names_by_schema(self) -> ta.Mapping[str, ta.FrozenSet[str]]:
        return col.MissingDict(lambda sn: frozenset(self._inspector.get_table_names(sn)))

    @properties.cached
    def tables(self) -> ta.Mapping[ta.Tuple[str, str], 'Inspection.Table']:
        return col.MissingDict(lambda t: self.Table(self, *t))

    class Table:

        def __init__(self, owner: 'Inspection', name: str, schema: str = None) -> None:
            super().__init__()
            self._owner = check.isinstance(owner, Inspection)
            self._name = check.non_empty_str(name)
            self._schema = check.non_empty_str(schema)

        @property
        def name(self) -> str:
            return self._name

        @property
        def schema(self) -> ta.Optional[str]:
            return self._schema

        # https://docs.sqlalchemy.org/en/13/core/reflection.html#fine-grained-reflection-with-inspector

        @properties.cached
        def options(self):
            return self._owner._inspector.get_table_options(self.name, self.schema)

        @properties.cached
        def columns(self):
            return self._owner._inspector.get_columns(self.name, self.schema)

        @properties.cached
        def primary_keys(self):
            return self._owner._inspector.get_primary_keys(self.name, self.schema)

        @properties.cached
        def pk_constraint(self):
            return self._owner._inspector.get_pk_constraint(self.name, self.schema)

        @properties.cached
        def foreign_keys(self):
            return self._owner._inspector.get_foreign_keys(self.name, self.schema)

        @properties.cached
        def indexes(self):
            return self._owner._inspector.get_indexes(self.name, self.schema)

        @properties.cached
        def unique_constraints(self):
            return self._owner._inspector.get_unique_constraints(self.name, self.schema)

        @properties.cached
        def table_comment(self):
            return self._owner._inspector.get_table_comment(self.name, self.schema)

        @properties.cached
        def check_constraints(self):
            return self._owner._inspector.get_check_constraints(self.name, self.schema)
