from .. import Q
from ..rendering import render


def test_render_select():
    query = Q.select(
        [
            1,
        ],
        'foo',
        Q.and_(
            Q.eq(Q.i('foo'), 1),
            Q.ne(Q.i('bar'), Q.add(Q.i('baz'), 2)),
        ),
    )

    print(query)
    print(render(query))


def test_render_insert():
    query = Q.insert(
        ['foo', 'bar'],
        'some_table',
        [123, 'abc'],
    )

    print(query)
    print(render(query))
