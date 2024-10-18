from .. import Q
from ..exprs import Param


def test_query():
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


def test_params():
    print(repr(Param()))
    print(repr(Param('foo')))
