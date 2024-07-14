from .. import simple as simple_


def test_nop():
    assert simple_.nop().encode(1) == 1
