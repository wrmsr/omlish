"""
TODO:
 - move to sql/alchemy/tabledefs.py
"""
import typing as ta

import sqlalchemy as sa
import sqlalchemy.sql.schema

from .tabledefs import TableDef


def build_sa_table(
        td: TableDef,
        *,
        metadata: sa.MetaData | None = None,
        **kwargs: ta.Any,
) -> sa.Table:
    items: list[sa.sql.schema.SchemaItem] = []

    return sa.Table(
        td.name,
        metadata if metadata is not None else sa.MetaData(),
        *items,
        **kwargs,
    )
