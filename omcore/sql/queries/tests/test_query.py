import pytest

from .. import Q
from ..base import NodeComparisonTypeError
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


def test_eq_type_error():
    def gen_q(n):
        return Q.select([Q.i.foo], Q.n.bar.baz, Q.eq(Q.i.name, n))

    n0 = gen_q('barf')
    n1 = gen_q('barf')
    n2 = gen_q('frab')

    with pytest.raises(NodeComparisonTypeError):
        n0 == n1  # noqa
    assert n1.eq(n0)
    assert n0.eq(n1)
    assert not n1.eq(n2)
    assert not n2.eq(n0)
