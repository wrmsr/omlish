from ..params import Param


def test_params_eq():
    p_anon_0 = Param()
    p_anon_1 = Param()

    p2_0 = Param('p2')
    p2_1 = Param('p2')

    p3 = Param('p3')

    assert p_anon_0 == p_anon_0
    assert not p_anon_0 == p_anon_1

    assert p2_0 == p2_0
    assert p2_0 == p2_1
    assert p2_1 == p2_0

    assert not p3 == p2_0
    assert not p2_0 == p3
    assert not p3 == p_anon_0

    assert not p2_0 == p_anon_0
    assert not p2_0 == p3
