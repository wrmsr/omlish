import contextlib

import sqlalchemy as sa

from .... import lang
from ... import api
from ... import queries
from ...queries import Q
from ..apiadapter import api_adapt


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

        db = api_adapt(engine)
        q = Q.select(
            [Q.i.name],
            Q.i.t1,
            Q.eq(Q.n.name, 'some name 1'),
        )
        with api.query(db, queries.render(q).s) as rows:
            lst = list(rows)

        assert len(lst) == 1
        assert lst[0]['name'] == 'some name 1'
