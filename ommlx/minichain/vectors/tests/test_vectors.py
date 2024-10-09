from ..vectors import Vector


def test_vector():
    v = Vector([1])
    assert Vector(v) is v
