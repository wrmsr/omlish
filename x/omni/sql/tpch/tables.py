import typing as ta

import sqlalchemy as sa

from ... import check
from ... import dataclasses as dc
from ... import tpch


SA_TYPES_BY_TPCH_TYPE = {
    tpch.ents.Column.Type.INTEGER: sa.Integer(),
    tpch.ents.Column.Type.IDENTIFIER: sa.Integer(),
    tpch.ents.Column.Type.DATE: sa.Date(),
    tpch.ents.Column.Type.DOUBLE: sa.Float(),
    tpch.ents.Column.Type.VARCHAR: sa.String(),
}


def build_sa_tables(*, metadata: ta.Optional[sa.MetaData] = None) -> ta.Sequence[sa.Table]:
    if metadata is None:
        metadata = sa.MetaData()
    check.isinstance(metadata, sa.MetaData)

    sats = []
    for ent in tpch.ents.ENTITIES:
        sacs = []
        for f in dc.fields(ent):
            if tpch.ents.Column not in f.metadata:
                continue
            tc = check.isinstance(f.metadata[tpch.ents.Column], tpch.ents.Column)
            meta = dc.metadatas_dict(ent)[tpch.ents.Meta]
            sac = sa.Column(tc.name, SA_TYPES_BY_TPCH_TYPE[tc.type], primary_key=f.name in meta.primary_key)
            sacs.append(sac)

        sat = sa.Table(ent.__name__.lower(), metadata, *sacs)
        sats.append(sat)

    return sats
