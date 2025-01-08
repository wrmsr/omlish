from .. import Q
from ..rendering import render


def test_render():
    for query in [
        Q.select(
            [1],
            Q.n.foo,
            Q.and_(
                Q.eq(Q.i.foo, 1),
                Q.ne(Q.i.bar, Q.add(Q.i.baz, 2)),
            ),
        ),

        Q.insert(
            ['foo', 'bar'],
            Q.n.some_schema.some_table,
            [123, 'abc'],
        ),

        Q.select([
            Q.p.foo,
            Q.p(),
            Q.p.bar,
            Q.p.foo,
        ]),

        Q.select(
            [
                Q.p.foo,
                Q.p.bar,
                Q.p.baz,
            ],
            Q.inner_join(
                Q.n.some_schema.some_table,
                Q.n.some_schema.some_other_table,
                Q.eq(Q.i.some_id, Q.i.some_other_id),
            ),
        ),
    ]:
        print(query)
        print(render(query))
        print()
