import contextlib

import sqlalchemy as sa

from omlish import lang

from .. import sql as tsql


def test_sql():
    md = sa.MetaData()
    tsql.build_sa_tables(metadata=md)

    with contextlib.ExitStack() as es:
        engine = sa.create_engine(f'sqlite://', echo=True)
        es.enter_context(lang.defer(engine.dispose))

        with engine.begin() as conn:
            md.create_all(bind=conn)
            tsql.populate_sa_tables(conn, md)
