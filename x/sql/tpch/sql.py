import itertools
import typing as ta

from omlish import check
from omlish import dataclasses as dc
import sqlalchemy as sa

from . import ents
from . import gens


SA_TYPES_BY_TPCH_TYPE = {
    ents.Column.Type.INTEGER: sa.Integer(),
    ents.Column.Type.IDENTIFIER: sa.Integer(),
    ents.Column.Type.DATE: sa.Date(),
    ents.Column.Type.DOUBLE: sa.Float(),
    ents.Column.Type.VARCHAR: sa.String(),
}


def build_sa_tables(*, metadata: ta.Optional[sa.MetaData] = None) -> ta.Sequence[sa.Table]:
    if metadata is None:
        metadata = sa.MetaData()
    check.isinstance(metadata, sa.MetaData)

    sats = []
    for ent in ents.ENTITIES:
        sacs = []
        for f in dc.fields(ent):
            if ents.Column not in f.metadata:
                continue
            tc = check.isinstance(f.metadata[ents.Column], ents.Column)
            meta = dc.get_merged_metadata(ent)[dc.UserMetadata][0][ents.Meta]  # FIXME: :|
            sac = sa.Column(tc.name, SA_TYPES_BY_TPCH_TYPE[tc.type], primary_key=f.name in meta.primary_key)
            sacs.append(sac)

        sat = sa.Table(ent.__name__.lower(), metadata, *sacs)
        sats.append(sat)

    return sats


def populate_sa_tables(conn: sa.engine.Connection, metadata: sa.MetaData) -> None:
    check.isinstance(conn, sa.engine.Connection)
    check.isinstance(metadata, sa.MetaData)

    for n, g in [
        ('region', gens.RegionGenerator()),
        ('customer', gens.CustomerGenerator(10, 1, 20)),
    ]:
        sat = check.single(t for t in metadata.tables.values() if t.name == n)
        dcts = []
        for e in itertools.islice(g, 100):
            dct = {}
            for f in dc.fields(e):
                try:
                    col = check.isinstance(f.metadata[ents.Column], ents.Column)
                except KeyError:
                    continue
                dct[col.name] = getattr(e, f.name)
            dcts.append(dct)
        conn.execute(sat.insert(), dcts)
