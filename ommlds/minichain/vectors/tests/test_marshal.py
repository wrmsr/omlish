import math

from omlish import marshal as msh

from ..types import Vector


def test_marshal_vector():
    v = Vector([1, 2, -1])
    assert len(v) == 3
    assert v[1] == 2

    mv = msh.marshal(v)
    v2 = msh.unmarshal(mv, Vector)

    assert all(math.isclose(e, e2) for e, e2 in zip(v2, v, strict=True))
