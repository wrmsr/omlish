from omlish.sql.queries import Q

from .. import sqleval as ev


def test_eval():
    q = Q.select(
        [Q.star],
        Q.n.t0,
        Q.eq(Q.n.id, 2),
    )

    print(ev.StmtEvaluator().eval(q))


def test_rels():
    q = Q.select(
        [Q.star],
        Q.default_join(
            Q.n.t0,
            Q.n.t1,
        ),
    )

    print(ev.StmtEvaluator().eval(q))
