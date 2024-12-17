from .. import Q
from ..params import Param


def test_query():
    query = Q.select(
        [
            1,
        ],
        Q.n.foo,
        Q.and_(
            Q.eq(Q.i.foo, Q.p.param_one),
            Q.ne(Q.i.bar, Q.add(Q.n.baz.qux, 2)),
        ),
    )

    print(query)


def test_params():
    print(repr(Param()))
    print(repr(Param('foo')))
