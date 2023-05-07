from .. import maybes


def test_maybe():
    m = maybes.just(10)
    assert m.must() == 10
