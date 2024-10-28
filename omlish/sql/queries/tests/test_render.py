from .. import Q
from ..rendering import render


def test_render():
    for query in [
        Q.select(
            [
                1,
            ],
            'foo',
            Q.and_(
                Q.eq(Q.i('foo'), 1),
                Q.ne(Q.i('bar'), Q.add(Q.i('baz'), 2)),
            ),
        ),
        Q.insert(
            ['foo', 'bar'],
            'some_table',
            [123, 'abc'],
        ),
    ]:
        print(query)
        print(render(query))
