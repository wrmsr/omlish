from .. import Q


def test_query():
    print(Q.select(
        [
            1,
        ],
        'foo',
        Q.and_(
            Q.eq(Q.i('foo'), 1),
            Q.ne(Q.i('bar'), Q.add(Q.i('baz'), 2)),
        ),
    ))
