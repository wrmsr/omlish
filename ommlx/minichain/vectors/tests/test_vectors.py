from ..vectors import Vector


def test_vector():
    v = Vector([1])
    assert Vector(v) is v

    assert len(Vector([1, 2, 3])) == 3
    assert Vector([1, 2, 3])[2] == 3.
