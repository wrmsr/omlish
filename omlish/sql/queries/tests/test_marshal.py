from .. import Q
from .... import marshal as msh
from ....formats import json
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

    print(json.dumps_pretty(msh.marshal(query, Node)))
