from .... import marshal as msh
from ....formats import json
from .. import Q
from ..base import Node


def test_marshal():
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

        Q.select(
            [Q.star],
            Q.n.barf,
        ),

        Q.update(
            Q.n.barf,
            {'foo': 123},
        ),

        Q.delete(
            Q.n.barf,
            Q.eq(Q.i.foo, 123),
        ),

        Q.select([Q.func('hi')]),

        Q.select(
            [Q.func(Q.k.count, Q.star)],
            Q.n.states,
            Q.eq(Q.n.key, 420),
        ),

        Q.select([Q.f.exists(Q.select(
            [1],
            Q.n.states,
            Q.eq(Q.n.key, 'foo'),
        ))]),
    ]:
        j = json.dumps_pretty(msh.marshal(query, Node))
        print(j)

        u = msh.unmarshal(json.loads(j), Node)
        assert u.eq(query)
