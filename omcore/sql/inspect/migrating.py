import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..api import querierfuncs as qf
from ..api.queriers import AsyncQuerier
from ..tabledefs.diffing import MigrationOp
from ..tabledefs.diffing import diff_table
from ..tabledefs.lower import lower_table_elements
from ..tabledefs.rendering import Renderer
from ..tabledefs.tabledefs import TableDef
from .inspectors import Inspector


##


@dc.dataclass(frozen=True)
class TableMigration(lang.Final):
    table: str

    _: dc.KW_ONLY

    created: bool = False
    ops: ta.Sequence[MigrationOp] = ()


async def migrate_table(
        querier: AsyncQuerier,
        table: TableDef,
        *,
        inspector: Inspector,
        renderer: Renderer,
) -> TableMigration:
    """
    Bring the live table named by `table` into line with the in-code definition: create it wholesale if absent,
    otherwise reflect it, diff the in-code definition against the reflection, and apply the resulting migration ops.

    Async-only, like the inspector it drives: a sync caller wraps its db/conn and runs this through `lang.sync_await`.
    Limited to the diff's supported subset (column / named-index add/drop); type, primary-key, and trigger changes are
    deliberately left untouched rather than mis-migrated.
    """

    table = lower_table_elements(table)

    reflected = await inspector.reflect_table(querier, table.name)
    if reflected is None:
        for s in renderer.render_create_statements(table):
            await qf.exec(querier, s)
        return TableMigration(table.name, created=True)

    ops = diff_table(table, inspector.lift_table(reflected))
    for op in ops:
        for s in renderer.render_migration(op):
            await qf.exec(querier, s)
    return TableMigration(table.name, ops=ops)
