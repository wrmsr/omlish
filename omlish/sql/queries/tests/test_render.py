from .. import Q
from ..rendering import render


def test_render():
    for query in [
        Q.select(
            [
                1,
            ],
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
        Q.select([Q.p.foo, Q.p(), Q.p.bar, Q.p.foo]),
    ]:
        print(query)
        print(render(query))
        print()
