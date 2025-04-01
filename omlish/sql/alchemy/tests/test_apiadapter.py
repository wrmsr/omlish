import contextlib

import sqlalchemy as sa

from ... import api
from .... import lang
from ...queries import Q


##


meta = sa.MetaData()
t1 = sa.Table(
    't1',
    meta,
    sa.Column('name', sa.String(50), primary_key=True),
)


##


def test_sqlite() -> None:
    with contextlib.ExitStack() as es:
        engine = sa.create_engine(f'sqlite://', echo=True)
        es.enter_context(lang.defer(engine.dispose))  # noqa

        with engine.begin() as conn:
            meta.drop_all(bind=conn)
            meta.create_all(bind=conn)

            conn.execute(
                t1.insert(), [
                    {'name': 'some name 1'},
                    {'name': 'some name 2'},
                ],
            )

        Q.select(
            [Q.i.name],
            Q.i.t1,
            Q.eq(Q.n.name, 'some name 1'),
        )

        with engine.connect() as conn:
            result = conn.execute(sa.select(t1).where(t1.c.name == 'some name 1'))
            rows = list(result.fetchall())
            assert len(rows) == 1
            assert rows[0].name == 'some name 1'

            print(conn.execute(sa.text('select sqlite_version()')).fetchall())
