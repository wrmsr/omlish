from .... import marshal as msh
from ....formats import json
from .. import Q
from ..base import Node


def test_marshal():
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

    j = json.dumps_pretty(msh.marshal(query, Node))
    print(j)

    u = msh.unmarshal(json.loads(j), Node)
    assert u == query
